using System;
using System.IO;
using System.Security;

namespace NepTunnel.Services
{
    public static class ScriptInjector
    {
        public static string GenerateRbxmxScript(string scriptName, string luauCode)
        {
            string xml = $@"<roblox xmlns:xmime=""http://www.w3.org/2005/05/xmlmime"" xmlns:xsi=""http://www.w3.org/2001/XMLSchema-instance"" xsi:noNamespaceSchemaLocation=""http://www.roblox.com/roblox.xsd"" version=""4"">
	<Meta name=""ExplicitAutoJoints"">true</Meta>
	<Item class=""Script"" referent=""RBXNepScript001"">
		<Properties>
			<BinaryString name=""AttributesSerialize""></BinaryString>
			<bool name=""Disabled"">false</bool>
			<Content name=""LinkedSource""><null></null></Content>
			<string name=""Name"">{SecurityElement.Escape(scriptName)}</string>
			<string name=""ScriptGuid"">{{{Guid.NewGuid().ToString().ToUpper()}}}</string>
			<ProtectedString name=""Source""><![CDATA[{luauCode}]]></ProtectedString>
			<int64 name=""SourceAssetId"">-1</int64>
			<BinaryString name=""Tags""></BinaryString>
		</Properties>
	</Item>
</roblox>";
            return xml;
        }

        public static (bool success, string message) InjectScriptIntoMap(string targetMapPath, string luauSource)
        {
            try
            {
                string rbxmxContent = GenerateRbxmxScript("NepNameSyncScript", luauSource);
                string stagedRbxmx = Path.Combine(ConfigManager.AppDataDir, "NepNameSyncScript.rbxmx");
                Directory.CreateDirectory(ConfigManager.AppDataDir);
                File.WriteAllText(stagedRbxmx, rbxmxContent);

                if (!string.IsNullOrWhiteSpace(targetMapPath) && File.Exists(targetMapPath))
                {
                    string ext = Path.GetExtension(targetMapPath).ToLowerInvariant();
                    if (ext == ".rbxlx")
                    {
                        string xmlContent = File.ReadAllText(targetMapPath);
                        if (xmlContent.Contains("NepNameSyncScript"))
                        {
                            return (true, "✓ El script 'NepNameSyncScript' ya está inyectado en este mapa.");
                        }

                        int sssIdx = xmlContent.IndexOf("class=\"ServerScriptService\"");
                        if (sssIdx > 0)
                        {
                            int insertIdx = xmlContent.IndexOf(">", sssIdx) + 1;
                            string itemXml = $"\n\t<Item class=\"Script\" referent=\"RBXNepSyncScript\">\n\t\t<Properties>\n\t\t\t<string name=\"Name\">NepNameSyncScript</string>\n\t\t\t<ProtectedString name=\"Source\"><![CDATA[{luauSource}]]></ProtectedString>\n\t\t</Properties>\n\t</Item>";
                            string newXml = xmlContent.Insert(insertIdx, itemXml);
                            File.WriteAllText(targetMapPath, newXml);
                            return (true, "✓ ¡Script inyectado exitosamente en ServerScriptService del mapa!");
                        }
                    }
                }

                // Stage via RbxmBridgeServer for automatic Studio import
                var (ok, msg) = RbxmBridgeServer.QueueRbxm(stagedRbxmx);
                if (ok)
                {
                    return (true, "✓ Script inyectado y preparado para importación automática al abrir Roblox Studio!");
                }

                return (true, $"✓ Script inyectado generado en: {stagedRbxmx}");
            }
            catch (Exception ex)
            {
                return (false, $"Error al inyectar script: {ex.Message}");
            }
        }
    }
}
