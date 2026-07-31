using System;
using System.IO;

namespace NepTunnel.Services
{
    // Automated Logging Service with Log Rotation, latest.log, and Roblox Studio C++ Log Extraction
    public static class Logger
    {
        public static string LogDir { get; } = Path.Combine(ConfigManager.AppDataDir, "logs");
        public static string LatestLogPath { get; } = Path.Combine(LogDir, "latest.log");

        static Logger()
        {
            try
            {
                Directory.CreateDirectory(LogDir);

                // Rotate previous latest.log if it exists and has content
                if (File.Exists(LatestLogPath))
                {
                    FileInfo fi = new FileInfo(LatestLogPath);
                    if (fi.Length > 0)
                    {
                        string timestamp = fi.LastWriteTime.ToString("yyyy-MM-dd_HH-mm-ss");
                        string archivedPath = Path.Combine(LogDir, $"log_{timestamp}.log");
                        if (!File.Exists(archivedPath))
                        {
                            File.Move(LatestLogPath, archivedPath);
                        }
                    }
                }

                // Initialize clean latest.log for current session
                File.WriteAllText(LatestLogPath, $"=== NepTunnel Session Log Started: {DateTime.Now:yyyy-MM-dd HH:mm:ss} ===\n\n");
            }
            catch { }
        }

        public static void Log(string message)
        {
            try
            {
                string line = $"[{DateTime.Now:HH:mm:ss}] {message}";
                File.AppendAllText(LatestLogPath, line + "\n");
                Console.WriteLine(line);
            }
            catch { }
        }

        public static void LogError(string message, Exception? ex = null)
        {
            string errStr = ex != null ? $"{message} | Exception: {ex.Message}\n{ex.StackTrace}" : message;
            Log($"[ERROR] {errStr}");
        }

        // Automatically scans Roblox's C++ logs directory (%LOCALAPPDATA%\Roblox\logs) and captures recent Studio output
        public static string? FetchLatestRobloxStudioLog()
        {
            try
            {
                string robloxLogDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Roblox", "logs");
                if (!Directory.Exists(robloxLogDir)) return null;

                var files = new DirectoryInfo(robloxLogDir).GetFiles("*.log");
                FileInfo? latestRobloxLog = null;
                DateTime maxTime = DateTime.MinValue;

                foreach (var f in files)
                {
                    if (f.LastWriteTime > maxTime)
                    {
                        maxTime = f.LastWriteTime;
                        latestRobloxLog = f;
                    }
                }

                if (latestRobloxLog != null && File.Exists(latestRobloxLog.FullName))
                {
                    using (var fs = new FileStream(latestRobloxLog.FullName, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
                    using (var sr = new StreamReader(fs))
                    {
                        string content = sr.ReadToEnd();
                        Log($"--- Captured Roblox Studio Log ({latestRobloxLog.Name}) ---");
                        Log(content);
                        return content;
                    }
                }
            }
            catch (Exception ex)
            {
                LogError("Failed to fetch Roblox Studio log", ex);
            }
            return null;
        }
    }
}
