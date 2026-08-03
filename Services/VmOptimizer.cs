using System;
using System.IO;
using System.Text.RegularExpressions;

namespace NepTunnel.Services
{
    /// <summary>
    /// VM Optimizer: Lowers Roblox Studio graphics to absolute minimum
    /// to save resources on virtual machines.
    /// Edits GlobalSettings_13.xml in the Roblox AppData folder.
    /// </summary>
    public static class VmOptimizer
    {
        private static readonly string SettingsFile = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "Roblox", "GlobalSettings_13.xml"
        );

        public static void ApplyMinGraphics()
        {
            if (!File.Exists(SettingsFile))
            {
                // Create a minimal settings file if it doesn't exist
                CreateMinimalSettings();
                return;
            }

            string content = File.ReadAllText(SettingsFile);

            // Lower quality level to 1 (minimum)
            content = SetOrAddSetting(content, "QualityLevel", "1");

            // Disable/minimize all heavy graphics settings
            content = SetOrAddSetting(content, "GraphicsQualityLevel", "1");
            content = SetOrAddSetting(content, "MeshDetail", "0");

            // Shadow settings
            content = SetOrAddSetting(content, "ShadowCasters", "false");
            content = SetOrAddSetting(content, "GlobalShadows", "false");
            content = SetOrAddSetting(content, "EnableLocalLights", "false");

            // Texture quality
            content = SetOrAddSetting(content, "TextureQuality", "0");

            // Reflection / Post-process
            content = SetOrAddSetting(content, "EnableSSAO", "false");
            content = SetOrAddSetting(content, "EnableDepthOfField", "false");
            content = SetOrAddSetting(content, "EnableBloom", "false");
            content = SetOrAddSetting(content, "EnableSunRays", "false");
            content = SetOrAddSetting(content, "EnableLightAttenuation", "false");

            // Framerate cap help
            content = SetOrAddSetting(content, "FrameRateManager", "1");

            File.WriteAllText(SettingsFile, content);
            Logger.Log("[VmOptimizer] Roblox Studio graphics set to minimum.");
        }

        private static string SetOrAddSetting(string xml, string key, string value)
        {
            // Try to replace an existing <key>...</key> or key="..." attribute
            string tagPattern = $@"(<{Regex.Escape(key)}[^>]*>)[^<]*(</{ Regex.Escape(key)}>)";
            if (Regex.IsMatch(xml, tagPattern, RegexOptions.IgnoreCase))
            {
                return Regex.Replace(xml, tagPattern, $"$1{value}$2", RegexOptions.IgnoreCase);
            }

            // Try attribute form: key="..."
            string attrPattern = $@"{Regex.Escape(key)}=""[^""]*""";
            if (Regex.IsMatch(xml, attrPattern, RegexOptions.IgnoreCase))
            {
                return Regex.Replace(xml, attrPattern, $"{key}=\"{value}\"", RegexOptions.IgnoreCase);
            }

            // Insert before closing </RobloxStudioGlobalSettings> or </Settings> tag
            foreach (string closing in new[] { "</RobloxStudioGlobalSettings>", "</Settings>", "</settings>" })
            {
                if (xml.Contains(closing))
                {
                    return xml.Replace(closing, $"\t<{key}>{value}</{key}>\n{closing}");
                }
            }

            return xml;
        }

        private static void CreateMinimalSettings()
        {
            Directory.CreateDirectory(Path.GetDirectoryName(SettingsFile)!);
            string minimal = @"<RobloxStudioGlobalSettings>
	<QualityLevel>1</QualityLevel>
	<GraphicsQualityLevel>1</GraphicsQualityLevel>
	<ShadowCasters>false</ShadowCasters>
	<GlobalShadows>false</GlobalShadows>
	<EnableLocalLights>false</EnableLocalLights>
	<TextureQuality>0</TextureQuality>
	<EnableSSAO>false</EnableSSAO>
	<EnableDepthOfField>false</EnableDepthOfField>
	<EnableBloom>false</EnableBloom>
	<EnableSunRays>false</EnableSunRays>
	<FrameRateManager>1</FrameRateManager>
</RobloxStudioGlobalSettings>";
            File.WriteAllText(SettingsFile, minimal);
            Logger.Log("[VmOptimizer] Created minimal Roblox Studio settings file.");
        }
    }
}
