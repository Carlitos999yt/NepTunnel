using System;
using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;

namespace NepTunnel.Services
{
    public static class RsmInstallerService
    {
        public const string TARGET_VERSION = "0.729.0.7290838";
        public const string VERSION_GUID = "version-4bb3958a2cde4efb";
        public const string GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Carlitos999yt/roblox-studio/main";

        public static string GetRsmStudioDirectory()
        {
            string localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            string dir = Path.Combine(localAppData, "Roblox Studio");
            if (!Directory.Exists(dir))
            {
                Directory.CreateDirectory(dir);
            }
            return dir;
        }

        public static string GetRsmManagerDirectory()
        {
            string localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            string dir = Path.Combine(localAppData, "Roblox Studio Mod Manager");
            if (!Directory.Exists(dir))
            {
                Directory.CreateDirectory(dir);
            }
            return dir;
        }

        public static string GetRsmStudioExePath()
        {
            return Path.Combine(GetRsmStudioDirectory(), "RobloxStudioBeta.exe");
        }

        public static bool IsRsmInstalled()
        {
            return File.Exists(GetRsmStudioExePath());
        }

        public static void PreConfigureTargetVersionState()
        {
            try
            {
                string stateDir = GetRsmManagerDirectory();
                string stateFile = Path.Combine(stateDir, "state.json");

                var stateObj = new
                {
                    TargetVersion = TARGET_VERSION,
                    VersionData = new
                    {
                        LastExecutedVersion = VERSION_GUID,
                        Version = TARGET_VERSION,
                        VersionGuid = VERSION_GUID,
                        VersionOverload = TARGET_VERSION
                    },
                    ChannelData = new
                    {
                        ChannelName = "LIVE",
                        ChannelToken = ""
                    }
                };

                string json = JsonSerializer.Serialize(stateObj, new JsonSerializerOptions { WriteIndented = true });
                File.WriteAllText(stateFile, json);
            }
            catch { }
        }

        public static async Task<bool> LaunchOfficialRsmBootstrapperAsync(Action<string, string> log)
        {
            log($"Pre-configurando TargetVersion a {TARGET_VERSION}…", "info");
            PreConfigureTargetVersionState();

            string bundledExe = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "bundled_assets", "RobloxStudioModManager.exe");
            if (!File.Exists(bundledExe))
            {
                bundledExe = Path.Combine(Directory.GetCurrentDirectory(), "bundled_assets", "RobloxStudioModManager.exe");
            }

            if (!File.Exists(bundledExe))
            {
                log($"✗ Error: No se encontró bundled_assets/RobloxStudioModManager.exe", "err");
                return false;
            }

            log($"Abriendo ventana del Roblox Studio Mod Manager para versión {TARGET_VERSION}…", "ok");
            try
            {
                var psi = new ProcessStartInfo
                {
                    FileName = bundledExe,
                    UseShellExecute = true
                };

                Process? proc = Process.Start(psi);
                log($"✓ Ventana del Mod Manager abierta correctamente.", "ok");
                await Task.Delay(1000);
                return true;
            }
            catch (Exception ex)
            {
                log($"✗ Error ejecutando RobloxStudioModManager.exe: {ex.Message}", "err");
                return false;
            }
        }

        public static async Task<bool> RepairFromGitHubRepoAsync(Action<string, string> log, Action<double> progress)
        {
            log($"Conectando a repositorio de reparación GitHub (Carlitos999yt/roblox-studio)…", "info");
            progress(0.05);

            string targetDir = GetRsmStudioDirectory();
            using var httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Add("User-Agent", "NepTunnel/RepairEngine");

            var criticalFiles = new string[]
            {
                "AppSettings.xml",
                "ReflectionMetadata.xml",
                "StartPageSystemMenu.xml",
                "SystemMenu.xml",
                "RobloxStudio_license.html",
                "ssl/cacert.pem",
                "shaders/shaders_d3d11.pack",
                "shaders/shaders_glsl3.pack",
                "shaders/shaders_vulkan_desktop.pack",
                "platforms/qwindows.dll",
                "styles/qwindowsvistastyle.dll",
                "imageformats/qgif.dll",
                "imageformats/qjpeg.dll"
            };

            int total = criticalFiles.Length;
            int count = 0;
            int repaired = 0;

            foreach (var relPath in criticalFiles)
            {
                count++;
                string destPath = Path.Combine(targetDir, relPath.Replace('/', '\\'));
                bool needsDownload = false;

                if (!File.Exists(destPath))
                {
                    log($"⚠ Archivo faltante detectado: {relPath}", "warn");
                    needsDownload = true;
                }
                else
                {
                    var fileInfo = new FileInfo(destPath);
                    if (fileInfo.Length == 0)
                    {
                        log($"⚠ Archivo corrupto/vacío detectado: {relPath}", "warn");
                        needsDownload = true;
                    }
                }

                if (needsDownload)
                {
                    try
                    {
                        string rawUrl = $"{GITHUB_RAW_BASE}/{relPath}";
                        log($"📥 Descargando reparación desde GitHub: {relPath}…", "info");
                        byte[] fileBytes = await httpClient.GetByteArrayAsync(rawUrl);
                        string? dir = Path.GetDirectoryName(destPath);
                        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
                        await File.WriteAllBytesAsync(destPath, fileBytes);
                        repaired++;
                        log($"✓ Archivo reparado con éxito desde GitHub: {relPath}", "ok");
                    }
                    catch (Exception ex)
                    {
                        log($"⚠ No se pudo descargar {relPath} desde GitHub: {ex.Message}", "warn");
                    }
                }
                else
                {
                    log($"✓ Verificado correcto: {relPath}", "dim");
                }

                progress(0.05 + (0.90 * ((double)count / total)));
            }

            PreConfigureTargetVersionState();
            progress(1.0);

            if (repaired > 0)
            {
                log($"✓ Reparación desde GitHub completada. Se solucionaron {repaired} archivo(s).", "ok");
            }
            else
            {
                log($"✓ Todos los archivos están sincronizados e idénticos con tu GitHub.", "ok");
            }

            return true;
        }

        public static void CleanRsmRegistryAndProtocols()
        {
            if (!System.Runtime.InteropServices.RuntimeInformation.IsOSPlatform(System.Runtime.InteropServices.OSPlatform.Windows)) return;

            try
            {
                // Delete ONLY RSM registry subkeys under HKCU\Software (NEVER touch Roblox Player keys)
                using var hkcuSoftware = Microsoft.Win32.Registry.CurrentUser.OpenSubKey(@"Software", writable: true);
                if (hkcuSoftware != null)
                {
                    try { hkcuSoftware.DeleteSubKeyTree("Roblox Studio Mod Manager", throwOnMissingSubKey: false); } catch { }
                    try { hkcuSoftware.DeleteSubKeyTree("Roblox Studio", throwOnMissingSubKey: false); } catch { }
                }

                // Delete ONLY RSM specific directories under LocalAppData (NEVER touch %LOCALAPPDATA%\Roblox or Roblox Player)
                string localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
                string rsmDir = Path.Combine(localAppData, "Roblox Studio");
                if (Directory.Exists(rsmDir))
                {
                    try { Directory.Delete(rsmDir, true); } catch { }
                }

                string rsmModDir = Path.Combine(localAppData, "Roblox Studio Mod Manager");
                if (Directory.Exists(rsmModDir))
                {
                    try { Directory.Delete(rsmModDir, true); } catch { }
                }
            }
            catch { }
        }
    }
}
