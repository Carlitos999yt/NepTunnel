using System;
using System.IO;

namespace NepTunnel.Services
{
    public static class PluginInstaller
    {
        public static bool EnsurePluginInstalled(out string statusMessage)
        {
            try
            {
                string localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
                string pluginsDir = Path.Combine(localAppData, "Roblox", "Plugins");
                Directory.CreateDirectory(pluginsDir);
                string destFile = Path.Combine(pluginsDir, "NepBridgePlugin.lua");

                bool alreadyExisted = File.Exists(destFile);

                string sourcePlugin = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "bundled_assets", "NepBridgePlugin.lua");
                if (File.Exists(sourcePlugin))
                {
                    File.Copy(sourcePlugin, destFile, true);
                    if (alreadyExisted)
                    {
                        statusMessage = "✓ Plugin e inyector de nombres reemplazado correctamente en Roblox Studio.";
                    }
                    else
                    {
                        statusMessage = "✓ Plugin e inyector de nombres instalado correctamente en Roblox Studio.";
                    }
                    Console.WriteLine($"[PluginInstaller] {statusMessage}");
                    return true;
                }
                else
                {
                    statusMessage = "✗ No se encontró el archivo del plugin original.";
                    return false;
                }
            }
            catch (Exception ex)
            {
                statusMessage = $"✗ Error al instalar el plugin: {ex.Message}";
                Console.WriteLine($"[PluginInstaller] {statusMessage}");
                return false;
            }
        }

        public static void EnsurePluginInstalled()
        {
            EnsurePluginInstalled(out _);
        }
    }
}
