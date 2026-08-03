using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace NepTunnel.Services
{
    // Model representing persistent application settings stored in nep_config.json.
    public class NepConfig
    {
        [JsonPropertyName("uid")]
        public string Uid { get; set; } = "1000";

        [JsonPropertyName("username")]
        public string Username { get; set; } = "";

        [JsonPropertyName("port")]
        public string Port { get; set; } = "55555";

        [JsonPropertyName("host_addr")]
        public string HostAddr { get; set; } = "";

        [JsonPropertyName("join_addr")]
        public string JoinAddr { get; set; } = "";

        [JsonPropertyName("addr")]
        public string Addr
        {
            get => HostAddr;
            set { HostAddr = value; }
        }

        [JsonPropertyName("studio")]
        public string Studio { get; set; } = "";

        [JsonPropertyName("map")]
        public string Map { get; set; } = "";

        [JsonPropertyName("import_scripts")]
        public bool ImportScripts { get; set; } = false;

        [JsonPropertyName("language")]
        public string Language { get; set; } = "en";

        [JsonPropertyName("saved_maps")]
        public List<string> SavedMaps { get; set; } = new List<string>();
    }

    // Handles configuration loading, saving, search path resolution, and session logging.
    public static class ConfigManager
    {
        public static string ScriptDir { get; } = AppDomain.CurrentDomain.BaseDirectory;
        public static string AppDataDir { get; } = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "NepTunnel");
        public static string LogFile { get; } = Path.Combine(AppDataDir, "SESSION_INFO.txt");
        public static string AssetsDir { get; } = Path.Combine(AppDataDir, "bundled_assets");

        // Returns all potential locations to read or write nep_config.json.
        private static List<string> GetConfigSearchPaths()
        {
            var paths = new List<string>();

            // 1. User LocalAppData directory (%LOCALAPPDATA%\NepTunnel\nep_config.json)
            string appDataConfig = Path.Combine(AppDataDir, "nep_config.json");
            paths.Add(appDataConfig);

            // 2. Current working directory
            string cwdConfig = Path.Combine(Directory.GetCurrentDirectory(), "nep_config.json");
            if (!paths.Contains(cwdConfig)) paths.Add(cwdConfig);

            // 3. Application BaseDirectory
            string baseConfig = Path.Combine(ScriptDir, "nep_config.json");
            if (!paths.Contains(baseConfig)) paths.Add(baseConfig);

            // 4. Parent workspace directories
            try
            {
                string p1 = Path.GetFullPath(Path.Combine(ScriptDir, "..", "..", "..", "nep_config.json"));
                if (!paths.Contains(p1)) paths.Add(p1);

                string p2 = Path.GetFullPath(Path.Combine(ScriptDir, "..", "..", "..", "..", "nep_config.json"));
                if (!paths.Contains(p2)) paths.Add(p2);
            }
            catch { }

            return paths;
        }

        public static List<string> BundledMaps { get; } = new List<string>();

        static ConfigManager()
        {
            InitBundledAssets();
        }

        // Copies bundled asset map files to the local assets directory if available.
        private static void InitBundledAssets()
        {
            string[] bundledFiles = new[] { "MapsforNepfile.rbxm", "CleanedAnimsNepFile.rbxm" };
            try
            {
                Directory.CreateDirectory(AssetsDir);
                foreach (var file in bundledFiles)
                {
                    string src = Path.Combine(ScriptDir, file);
                    string dst = Path.Combine(AssetsDir, file);
                    if (File.Exists(src))
                    {
                        try
                        {
                            FileInfo srcInfo = new FileInfo(src);
                            FileInfo dstInfo = new FileInfo(dst);
                            if (!dstInfo.Exists || srcInfo.Length != dstInfo.Length)
                            {
                                File.Copy(src, dst, true);
                            }
                            BundledMaps.Add(dst);
                        }
                        catch { }
                    }
                }
            }
            catch { }
        }

        // Reads nep_config.json from disk or returns default configuration.
        public static NepConfig LoadConfig()
        {
            var config = new NepConfig();
            var searchPaths = GetConfigSearchPaths();

            foreach (var cfgPath in searchPaths)
            {
                try
                {
                    if (File.Exists(cfgPath))
                    {
                        string json = File.ReadAllText(cfgPath);
                        var loaded = JsonSerializer.Deserialize<NepConfig>(json);
                        if (loaded != null)
                        {
                            config = loaded;
                            break;
                        }
                    }
                }
                catch { }
            }

            // Inject bundled maps so they are always available in saved maps list
            foreach (var bMap in BundledMaps)
            {
                if (!config.SavedMaps.Contains(bMap))
                {
                    config.SavedMaps.Insert(0, bMap);
                }
            }

            return config;
        }

        // Saves current application configuration to nep_config.json across search locations.
        public static void SaveConfig(NepConfig config)
        {
            try
            {
                var options = new JsonSerializerOptions { WriteIndented = true };
                string json = JsonSerializer.Serialize(config, options);

                try { Directory.CreateDirectory(AppDataDir); } catch { }

                var searchPaths = GetConfigSearchPaths();
                foreach (var cfgPath in searchPaths)
                {
                    try
                    {
                        string? dir = Path.GetDirectoryName(cfgPath);
                        if (!string.IsNullOrEmpty(dir))
                        {
                            Directory.CreateDirectory(dir);
                            File.WriteAllText(cfgPath, json);
                        }
                    }
                    catch { }
                }
            }
            catch { }
        }

        // Writes active session command lines to SESSION_INFO.txt for user reference.
        public static string WriteSessionLog(string pg, string tg, string tunnelAddr, string port, string uid)
        {
            string host, dp;
            if (tunnelAddr.Contains(':'))
            {
                var parts = tunnelAddr.Split(':', 2);
                host = parts[0];
                dp = parts[1];
            }
            else
            {
                host = tunnelAddr;
                dp = port;
            }

            string winCmd = $"powershell -ExecutionPolicy Bypass -Command " +
                            $"\"$p = Get-ChildItem -Path $env:LOCALAPPDATA\\Roblox\\Versions " +
                            $"-Filter RobloxStudioBeta.exe -Recurse | Select-Object -First 1 " +
                            $"-ExpandProperty FullName; Start-Process -FilePath $p -ArgumentList " +
                            $"'-task StartClient -placeId 0 -universeId 0 -placeVersion 0 " +
                            $"-server {host} -port {dp} -parentSessionGuid {pg} " +
                            $"-playTestSessionGuid {tg} -instanceId StudioPlayer_0'\"";

            string macCmd = $"\"/Applications/RobloxStudio.app/Contents/MacOS/RobloxStudio\" " +
                            $"-task StartClient -placeId 0 -universeId 0 -placeVersion 0 " +
                            $"-server {host} -port {dp} -parentSessionGuid {pg} " +
                            $"-playTestSessionGuid {tg} -instanceId StudioPlayer_0";

            string linCmd = $"flatpak run org.vinegarhq.Vinegar studio -- " +
                            $"-task StartClient -placeId 0 -universeId 0 -placeVersion 0 " +
                            $"-server {host} -port {dp} -parentSessionGuid {pg} " +
                            $"-playTestSessionGuid {tg} -instanceId StudioPlayer_0";

            var lines = new List<string>
            {
                "==========================================================",
                "  NEP TUNNEL - ROBLOX STUDIO SESSION LOG                  ",
                "==========================================================",
                $"Date       : {DateTime.Now:yyyy-MM-dd HH:mm:ss}",
                $"User ID    : {uid}",
                $"Address    : {tunnelAddr}",
                $"Server Local Port: {port}",
                "",
                "-- WINDOWS (Command Prompt) --",
                winCmd,
                "",
                "-- MAC (Terminal) --",
                macCmd,
                "",
                "-- LINUX / VINEGAR --",
                linCmd,
                "",
                "=========================================================="
            };

            try
            {
                File.WriteAllLines(LogFile, lines);
            }
            catch { }

            return winCmd;
        }
    }
}
