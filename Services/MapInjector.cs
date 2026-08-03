using System;
using System.IO;
using System.Runtime.InteropServices;

namespace NepTunnel.Services
{
    public static class MapInjector
    {
        public static string GetRuntimeServerPlace()
        {
            if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
            {
                string baseDir = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
                return Path.Combine(baseDir, "Roblox", "server.rbxl");
            }
            else if (RuntimeInformation.IsOSPlatform(OSPlatform.OSX))
            {
                string home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
                return Path.Combine(home, "Library", "Application Support", "Roblox", "server.rbxl");
            }
            else if (RuntimeInformation.IsOSPlatform(OSPlatform.Linux))
            {
                string home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
                return Path.Combine(home, ".var", "app", "org.vinegarhq.Vinegar", "data", "Roblox", "server.rbxl");
            }
            return "";
        }

        public static bool InjectMap(string mapPath)
        {
            if (string.IsNullOrWhiteSpace(mapPath) || !File.Exists(mapPath))
            {
                string defaultMap = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "bundled_assets", "default_baseplate.rbxlx");
                if (File.Exists(defaultMap))
                {
                    mapPath = defaultMap;
                }
                else
                {
                    return false;
                }
            }

            string target = GetRuntimeServerPlace();
            if (string.IsNullOrEmpty(target))
            {
                return false;
            }

            try
            {
                string? dir = Path.GetDirectoryName(target);
                if (!string.IsNullOrEmpty(dir))
                {
                    Directory.CreateDirectory(dir);
                }

                if (File.Exists(target))
                {
                    try { File.Delete(target); } catch { }
                }

                File.Copy(mapPath, target, true);
                Console.WriteLine($"[MapInjector] Successfully injected map: {mapPath} -> {target}");
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[MapInjector] Failed to inject: {ex.Message}");
                return false;
            }
        }
    }
}
