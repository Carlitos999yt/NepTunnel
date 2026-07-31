using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;

namespace NepTunnel.Services
{
    public static class RobloxStudioService
    {
        public const string VINEGAR = "__VINEGAR__";

        public record StudioInstallation(string Name, string Path, string Type, bool IsRecommended);

        private static IEnumerable<string> SafeGetFiles(string rootPath, string searchPattern)
        {
            var pending = new Queue<string>();
            pending.Enqueue(rootPath);
            while (pending.Count > 0)
            {
                string currentDir = pending.Dequeue();
                string[] files = Array.Empty<string>();
                try
                {
                    files = Directory.GetFiles(currentDir, searchPattern);
                }
                catch { }

                foreach (var file in files)
                {
                    yield return file;
                }

                string[] subDirs = Array.Empty<string>();
                try
                {
                    subDirs = Directory.GetDirectories(currentDir);
                }
                catch { }

                foreach (var subDir in subDirs)
                {
                    pending.Enqueue(subDir);
                }
            }
        }

        public static List<StudioInstallation> GetDetectedStudioInstallations()
        {
            var list = new List<StudioInstallation>();
            try
            {
                if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
                {
                    string localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
                    string programFiles = Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86);

                    // 1. RSM (Roblox Studio Mod Manager)
                    string rsmDir = Path.Combine(localAppData, "Roblox Studio");
                    if (Directory.Exists(rsmDir))
                    {
                        var files = SafeGetFiles(rsmDir, "RobloxStudioBeta.exe")
                                             .OrderByDescending(f => { try { return File.GetLastWriteTime(f); } catch { return DateTime.MinValue; } });
                        foreach (var f in files)
                        {
                            if (!list.Any(i => i.Path.Equals(f, StringComparison.OrdinalIgnoreCase)))
                            {
                                list.Add(new StudioInstallation("Roblox Studio RSM (Mod Manager)", f, "RSM", true));
                            }
                        }
                    }

                    string rsmAltDir = Path.Combine(localAppData, "Roblox Studio Mod Manager");
                    if (Directory.Exists(rsmAltDir))
                    {
                        var files = SafeGetFiles(rsmAltDir, "RobloxStudioBeta.exe")
                                             .OrderByDescending(f => { try { return File.GetLastWriteTime(f); } catch { return DateTime.MinValue; } });
                        foreach (var f in files)
                        {
                            if (!list.Any(i => i.Path.Equals(f, StringComparison.OrdinalIgnoreCase)))
                            {
                                list.Add(new StudioInstallation("Roblox Studio RSM (Mod Manager)", f, "RSM", true));
                            }
                        }
                    }

                    // 2. Bloxstrap Roblox Studio
                    string bloxstrapDir = Path.Combine(localAppData, "Bloxstrap", "Versions");
                    if (Directory.Exists(bloxstrapDir))
                    {
                        var files = SafeGetFiles(bloxstrapDir, "RobloxStudioBeta.exe")
                                             .OrderByDescending(f => { try { return File.GetLastWriteTime(f); } catch { return DateTime.MinValue; } });
                        foreach (var f in files)
                        {
                            if (!list.Any(i => i.Path.Equals(f, StringComparison.OrdinalIgnoreCase)))
                            {
                                list.Add(new StudioInstallation($"Bloxstrap Studio ({Path.GetFileName(Path.GetDirectoryName(f))})", f, "Bloxstrap", false));
                            }
                        }
                    }

                    // 3. Roblox Studio Oficial Standard
                    string versionsDir = Path.Combine(localAppData, "Roblox", "Versions");
                    if (Directory.Exists(versionsDir))
                    {
                        var files = SafeGetFiles(versionsDir, "RobloxStudioBeta.exe")
                                             .OrderByDescending(f => { try { return File.GetLastWriteTime(f); } catch { return DateTime.MinValue; } });
                        foreach (var f in files)
                        {
                            if (!list.Any(i => i.Path.Equals(f, StringComparison.OrdinalIgnoreCase)))
                            {
                                list.Add(new StudioInstallation($"Roblox Studio Oficial ({Path.GetFileName(Path.GetDirectoryName(f))})", f, "Oficial", false));
                            }
                        }
                    }

                    string pfVersions = Path.Combine(programFiles, "Roblox", "Versions");
                    if (Directory.Exists(pfVersions))
                    {
                        var files = SafeGetFiles(pfVersions, "RobloxStudioBeta.exe")
                                             .OrderByDescending(f => { try { return File.GetLastWriteTime(f); } catch { return DateTime.MinValue; } });
                        foreach (var f in files)
                        {
                            if (!list.Any(i => i.Path.Equals(f, StringComparison.OrdinalIgnoreCase)))
                            {
                                list.Add(new StudioInstallation("Roblox Studio Oficial (Program Files)", f, "Oficial", false));
                            }
                        }
                    }
                }
            }
            catch { }
            return list.OrderByDescending(i =>
            {
                try { return File.GetLastWriteTime(i.Path); } catch { return DateTime.MinValue; }
            }).ToList();
        }

        private static readonly List<Process> _spawnedProcesses = new();
        private static readonly object _procLock = new();

        public static string GetStudioPath()
        {
            if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
            {
                var installs = GetDetectedStudioInstallations();
                if (installs.Count > 0)
                {
                    // Pick the installation with the latest File.GetLastWriteTime
                    var latest = installs.OrderByDescending(i =>
                    {
                        try { return File.GetLastWriteTime(i.Path); } catch { return DateTime.MinValue; }
                    }).FirstOrDefault();

                    if (latest != null && File.Exists(latest.Path))
                    {
                        return latest.Path;
                    }
                }

                string localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
                string alt = Path.Combine(localAppData, "Roblox", "RobloxStudioBeta.exe");
                if (File.Exists(alt))
                {
                    return alt;
                }
            }
            else if (RuntimeInformation.IsOSPlatform(OSPlatform.OSX))
            {
                string p1 = "/Applications/RobloxStudio.app/Contents/MacOS/RobloxStudio";
                string p2 = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Applications/RobloxStudio.app/Contents/MacOS/RobloxStudio");
                if (File.Exists(p1)) return p1;
                if (File.Exists(p2)) return p2;

                string userLib = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Library", "Application Support", "Roblox", "Versions");
                if (Directory.Exists(userLib))
                {
                    var files = Directory.GetFiles(userLib, "RobloxStudio", SearchOption.AllDirectories)
                                         .OrderBy(f => File.GetLastWriteTime(f))
                                         .ToList();
                    if (files.Count > 0) return files.Last();
                }
            }
            else if (RuntimeInformation.IsOSPlatform(OSPlatform.Linux))
            {
                try
                {
                    var psi = new ProcessStartInfo("flatpak", "info org.vinegarhq.Vinegar")
                    {
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        UseShellExecute = false,
                        CreateNoWindow = true
                    };
                    using var proc = Process.Start(psi);
                    proc?.WaitForExit(5000);
                    if (proc != null && proc.ExitCode == 0)
                    {
                        return VINEGAR;
                    }
                }
                catch { }
            }

            return "";
        }

        private static ProcessStartInfo BuildCmd(string studio, List<string> args)
        {
            if (studio == VINEGAR)
            {
                var fullArgs = new List<string> { "run", "org.vinegarhq.Vinegar", "studio", "--" };
                fullArgs.AddRange(args);
                var psi = new ProcessStartInfo("flatpak")
                {
                    UseShellExecute = false
                };
                foreach (var a in fullArgs) psi.ArgumentList.Add(a);
                return psi;
            }
            else
            {
                var psi = new ProcessStartInfo(studio)
                {
                    UseShellExecute = false
                };
                foreach (var a in args) psi.ArgumentList.Add(a);
                return psi;
            }
        }

        public static Action<string, string>? OnStudioError;

        public static void LaunchServer(string studio, string port, string uid, string pg, string tg)
        {
            var args = new List<string>
            {
                "-task", "StartServer",
                "-placeId", "0",
                "-universeId", "0",
                "-placeVersion", "0",
                "-port", port,
                "-creatorId", uid,
                "-creatorType", "1",
                "-numTestServerPlayersUponStartup", "1",
                "-userid", uid,
                "-parentSessionGuid", pg,
                "-playTestSessionGuid", tg,
                "-instanceId", "StudioServer"
            };

            var psi = BuildCmd(studio, args);

            try
            {
                var proc = Process.Start(psi);
                if (proc != null)
                {
                    proc.EnableRaisingEvents = true;
                    proc.Exited += (s, e) =>
                    {
                        try
                        {
                            int exitCode = proc.ExitCode;
                            if (exitCode != 0)
                            {
                                OnStudioError?.Invoke($"⚠ Roblox Studio Server exited unexpectedly (Exit Code: 0x{exitCode:X8})", "err");
                                OnStudioError?.Invoke("  Possible cause: Roblox cloud API degradation or corrupt map file.", "warn");
                            }
                        }
                        catch { }
                    };

                    lock (_procLock)
                    {
                        _spawnedProcesses.Add(proc);
                    }
                }
            }
            catch (Exception ex)
            {
                OnStudioError?.Invoke($"✗ Failed to launch Studio Server: {ex.Message}", "err");
            }
        }

        public static void LaunchClient(string studio, string server, string port, string pg, string tg, string uid = "1000", string inst = "StudioPlayer_0")
        {
            var args = new List<string>
            {
                "-task", "StartClient",
                "-placeId", "0",
                "-universeId", "0",
                "-placeVersion", "0",
                "-server", server,
                "-port", port,
                "-userid", string.IsNullOrWhiteSpace(uid) ? "1000" : uid,
                "-parentSessionGuid", pg,
                "-playTestSessionGuid", tg,
                "-instanceId", inst
            };

            var psi = BuildCmd(studio, args);

            try
            {
                var proc = Process.Start(psi);
                if (proc != null)
                {
                    proc.EnableRaisingEvents = true;
                    proc.Exited += (s, e) =>
                    {
                        try
                        {
                            int exitCode = proc.ExitCode;
                            if (exitCode != 0)
                            {
                                OnStudioError?.Invoke($"⚠ Roblox Studio Client exited unexpectedly (Exit Code: 0x{exitCode:X8})", "err");
                                OnStudioError?.Invoke("  Possible cause: Remote Host closed connection or invalid tunnel port.", "warn");
                            }
                        }
                        catch { }
                    };

                    lock (_procLock)
                    {
                        _spawnedProcesses.Add(proc);
                    }
                }
            }
            catch (Exception ex)
            {
                OnStudioError?.Invoke($"✗ Failed to launch Studio Client: {ex.Message}", "err");
            }
        }

        public static void StopAllStudioProcesses()
        {
            lock (_procLock)
            {
                foreach (var proc in _spawnedProcesses)
                {
                    try
                    {
                        if (!proc.HasExited)
                        {
                            proc.CloseMainWindow();
                            if (!proc.WaitForExit(1500))
                            {
                                proc.Kill(entireProcessTree: true);
                            }
                        }
                    }
                    catch { }
                }
                _spawnedProcesses.Clear();
            }
        }
    }
}
