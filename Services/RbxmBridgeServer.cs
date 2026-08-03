using System;
using System.Collections.Concurrent;
using System.IO;
using System.Net;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Threading.Tasks;

namespace NepTunnel.Services
{
    public static class RbxmBridgeServer
    {
        public const int BRIDGE_PORT = 7878;
        private static readonly string StagingDir = Path.Combine(Path.GetTempPath(), "rbxm_bridge");
        private static string? _bridgePending = null;
        private static readonly object LockObj = new object();
        private static HttpListener? _listener = null;
        private static bool _isRunning = false;

        public static string ActiveUsername { get; set; } = "Player";
        public static string ActiveUid { get; set; } = "1000";
        public static bool ScriptsImported { get; set; } = false;
        public static bool ForceScriptImport { get; set; } = false;

        private static readonly ConcurrentQueue<string> ClientNicknamesQueue = new();

        public static void RegisterClientNickname(string nickname)
        {
            if (!string.IsNullOrWhiteSpace(nickname) && nickname != "Player" && nickname != "<ur user id here>")
            {
                ClientNicknamesQueue.Enqueue(nickname.Trim());
                Logger.Log($"[Bridge] Registered remote client nickname: '{nickname.Trim()}'");
            }
        }

        public static bool IsRunning => _isRunning;

        public static bool Start()
        {
            if (_isRunning) return true;

            try
            {
                Directory.CreateDirectory(StagingDir);
                _listener = new HttpListener();
                _listener.Prefixes.Add($"http://127.0.0.1:{BRIDGE_PORT}/");
                _listener.Start();
                _isRunning = true;

                Task.Run(ListenLoop);
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[bridge] Start error: {ex.Message}");
                _isRunning = false;
                return false;
            }
        }

        private static async Task ListenLoop()
        {
            while (_isRunning && _listener != null && _listener.IsListening)
            {
                try
                {
                    var context = await _listener.GetContextAsync();
                    _ = Task.Run(() => HandleRequest(context));
                }
                catch
                {
                    if (!_isRunning) break;
                }
            }
        }

        private static void SendJson(HttpListenerResponse res, int statusCode, object obj)
        {
            try
            {
                string json = JsonSerializer.Serialize(obj);
                byte[] bytes = Encoding.UTF8.GetBytes(json);

                res.StatusCode = statusCode;
                res.ContentType = "application/json";
                res.ContentLength64 = bytes.Length;
                res.AddHeader("Access-Control-Allow-Origin", "*");
                res.OutputStream.Write(bytes, 0, bytes.Length);
                res.Close();
            }
            catch { }
        }

        private static void HandleRequest(HttpListenerContext context)
        {
            var req = context.Request;
            var res = context.Response;

            if (req.HttpMethod == "OPTIONS")
            {
                res.StatusCode = 204;
                res.AddHeader("Access-Control-Allow-Origin", "*");
                res.AddHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
                res.AddHeader("Access-Control-Allow-Headers", "Content-Type");
                res.Close();
                return;
            }

            string rawPath = req.Url?.AbsolutePath ?? "/";

            if (req.HttpMethod == "GET")
            {
                if (rawPath == "/identity" || rawPath == "/user")
                {
                    string queryRole = req.QueryString["role"] ?? "";
                    string targetName;

                    if (queryRole == "host")
                    {
                        targetName = string.IsNullOrWhiteSpace(ActiveUsername) ? "Player" : ActiveUsername;
                    }
                    else if (queryRole == "client" || queryRole == "next")
                    {
                        if (ClientNicknamesQueue.TryDequeue(out var clientNick))
                        {
                            targetName = clientNick;
                        }
                        else
                        {
                            targetName = "Player";
                        }
                    }
                    else
                    {
                        // Default logic: Dequeue client if available, else host username
                        if (ClientNicknamesQueue.TryDequeue(out var clientNick))
                        {
                            targetName = clientNick;
                        }
                        else
                        {
                            targetName = string.IsNullOrWhiteSpace(ActiveUsername) ? "Player" : ActiveUsername;
                        }
                    }

                    string safeUid = string.IsNullOrWhiteSpace(ActiveUid) ? "1000" : ActiveUid;
                    bool doForce = ForceScriptImport;
                    ForceScriptImport = false; // Reset one-shot trigger!

                    Logger.Log($"[Bridge] Roblox Studio queried identity (role='{queryRole}') -> Name: '{targetName}', UID: '{safeUid}', force='{doForce}'");
                    SendJson(res, 200, new
                    {
                        status = "ok",
                        name = targetName,
                        displayName = targetName,
                        uid = safeUid,
                        imported = ScriptsImported,
                        force_import = doForce
                    });
                }
                else if (rawPath == "/poll")
                {
                    string? pending;
                    lock (LockObj)
                    {
                        pending = _bridgePending;
                    }

                    if (pending == null)
                    {
                        SendJson(res, 200, new { status = "idle" });
                    }
                    else
                    {
                        SendJson(res, 200, new
                        {
                            status = "ready",
                            name = pending,
                            staging_dir = StagingDir
                        });
                    }
                }
                else if (rawPath == "/download")
                {
                    string? fname;
                    lock (LockObj)
                    {
                        fname = _bridgePending;
                    }

                    if (fname == null)
                    {
                        SendJson(res, 404, new { error = "no file pending" });
                        return;
                    }

                    // Security: Path Traversal Guard
                    string safeFileName = Path.GetFileName(fname);
                    string fpath = Path.GetFullPath(Path.Combine(StagingDir, safeFileName));
                    string safeDir = Path.GetFullPath(StagingDir);

                    if (!fpath.StartsWith(safeDir, StringComparison.OrdinalIgnoreCase) || !File.Exists(fpath))
                    {
                        SendJson(res, 404, new { error = "staged file missing or invalid" });
                        return;
                    }

                    try
                    {
                        byte[] data = File.ReadAllBytes(fpath);
                        res.StatusCode = 200;
                        res.ContentType = "application/octet-stream";
                        res.ContentLength64 = data.Length;
                        res.AddHeader("Content-Disposition", $"attachment; filename=\"{safeFileName}\"");
                        res.AddHeader("Access-Control-Allow-Origin", "*");
                        res.OutputStream.Write(data, 0, data.Length);
                        res.Close();
                    }
                    catch (Exception ex)
                    {
                        SendJson(res, 500, new { error = ex.Message });
                    }
                }
                else
                {
                    SendJson(res, 404, new { error = "not found" });
                }
            }
            else if (req.HttpMethod == "POST")
            {
                try
                {
                    using var reader = new StreamReader(req.InputStream, req.ContentEncoding);
                    string bodyStr = reader.ReadToEnd();
                    var node = JsonNode.Parse(bodyStr);

                    if (rawPath == "/queue")
                    {
                        string src = node?["path"]?.ToString() ?? "";

                        // Security: File extension validation (.rbxm / .rbxmx only)
                        string ext = Path.GetExtension(src).ToLowerInvariant();
                        if (ext != ".rbxm" && ext != ".rbxmx")
                        {
                            SendJson(res, 400, new { error = "invalid file type: only .rbxm and .rbxmx supported" });
                            return;
                        }

                        if (!File.Exists(src))
                        {
                            SendJson(res, 400, new { error = $"file not found: {src}" });
                            return;
                        }

                        string fname = Path.GetFileName(src);
                        string dst = Path.Combine(StagingDir, fname);
                        File.Copy(src, dst, true);

                        lock (LockObj)
                        {
                            _bridgePending = fname;
                        }

                        SendJson(res, 200, new { status = "queued", staged = dst });
                    }
                    else if (rawPath == "/clear")
                    {
                        lock (LockObj)
                        {
                            _bridgePending = null;
                        }
                        SendJson(res, 200, new { status = "cleared" });
                    }
                    else
                    {
                        SendJson(res, 404, new { error = "not found" });
                    }
                }
                catch (Exception ex)
                {
                    SendJson(res, 500, new { error = ex.Message });
                }
            }
            else
            {
                SendJson(res, 404, new { error = "not found" });
            }
        }

        public static (bool ok, string message) QueueRbxm(string path)
        {
            string ext = Path.GetExtension(path).ToLowerInvariant();
            if (ext != ".rbxm" && ext != ".rbxmx")
            {
                return (false, "Only .rbxm and .rbxmx files are allowed");
            }

            if (!File.Exists(path))
            {
                return (false, "File not found");
            }

            Start();
            string fname = Path.GetFileName(path);
            string dst = Path.Combine(StagingDir, fname);
            try
            {
                File.Copy(path, dst, true);
            }
            catch (Exception ex)
            {
                return (false, ex.Message);
            }

            lock (LockObj)
            {
                _bridgePending = fname;
            }

            return (true, fname);
        }

        public static void Stop()
        {
            _isRunning = false;
            try
            {
                _listener?.Stop();
                _listener?.Close();
            }
            catch { }
            _listener = null;
        }
    }
}
