using System.Collections.Generic;
using System.Globalization;

namespace NepTunnel.Services
{
    public static class LocalizationService
    {
        public static string CurrentLanguage { get; set; } = "en"; // "en", "es", "pt"

        public static string DetectDefaultSystemLanguage()
        {
            try
            {
                string sysLang = CultureInfo.CurrentUICulture.TwoLetterISOLanguageName.ToLower();
                return sysLang switch
                {
                    "es" => "es",
                    "pt" => "pt",
                    _ => "en"
                };
            }
            catch
            {
                return "en";
            }
        }

        private static readonly Dictionary<string, Dictionary<string, string>> Translations = new()
        {
            ["en"] = new()
            {
                ["main_title"] = "What do you want to do?",
                ["main_subtitle"] = "Host or join a session via tunnel",
                ["btn_host"] = "HOST SESSION",
                ["btn_join"] = "JOIN SESSION",
                ["btn_echo"] = "ECHO TEST",
                ["btn_rbxm"] = "RBXM IMPORTER",
                ["btn_rsm_assistant"] = "RSM ASSISTANT",
                ["lbl_studio"] = "Studio:",
                ["lbl_tunnel_addr"] = "Tunnel Address:",
                ["lbl_server_port"] = "Server Local Port:",
                ["lbl_uid"] = "User ID:",
                ["lbl_username"] = "My Username / Nick (Optional):",
                ["lbl_proxy_port"] = "Proxy Port:",
                ["lbl_platform"] = "Platform:",
                ["lbl_bridge"] = "Studio Bridge:",
                ["browse"] = "Browse",
                ["btn_copy_script"] = "Copy Script",
                ["btn_inject_script"] = "Inject Script",
                ["back"] = "Back",
                ["test"] = "Test",

                // Host Config View
                ["host_title"] = "HOST SESSION",
                ["host_sub"] = "Review config, select map, and launch your server",
                ["lbl_map_file"] = "Map File (Optional)",
                ["btn_launch_server"] = "Launch Server",
                ["btn_tutorial"] = "Tutorial",

                // Host Running View
                ["host_console_title"] = "SERVER CONSOLE",
                ["btn_join_locally"] = "JOIN LOCALLY",
                ["btn_stop_back"] = "Stop & Back",

                // Join Config View
                ["join_title"] = "JOIN SESSION",
                ["join_sub"] = "Enter the host's tunnel address",
                ["lbl_tunnel_input"] = "Tunnel Address (host:port)",
                ["lbl_proxy_hint"] = "Will proxy via 127.0.0.1:55555 → remote address",
                ["btn_connect_launch"] = "Connect & Launch",

                // Join Running View
                ["join_console_title"] = "CONNECTION CONSOLE",
                ["btn_disc_back"] = "Disconnect & Back",

                // Echo Test View
                ["echo_title"] = "ECHO TEST",
                ["echo_sub"] = "Verify tunnel connectivity before starting a session",
                ["lbl_studio_port_host"] = "Studio Port (host)",
                ["lbl_tunnel_addr_joiner"] = "Tunnel Address (joiner)",
                ["btn_host_start_echo"] = "Host: Start Echo",
                ["btn_host_stop_echo"] = "Host: Stop Echo",
                ["btn_join_run_echo"] = "Join: Run Echo",
                ["echo_how_to_use"] = "HOW TO USE:\n  HOST:   Set port above, press \"Host: Start Echo\"\n  JOINER: Enter tunnel address above, press \"Join: Run Echo\"\n\n  This test sends packets directly to the tunnel.\n  It may take 3-5 seconds for the tunnel to \"wake up\".",

                // Rbxm Importer View
                ["rbxm_title"] = "RBXM IMPORTER",
                ["rbxm_sub"] = "Pick .rbxm files and send them to Studio via the bridge plugin",
                ["rbxm_empty"] = "No files saved yet. Click + Add .rbxm to get started.",
                ["btn_add_rbxm"] = "+ Add .rbxm",
                ["btn_send_studio"] = "Send to Studio",
                ["rbxm_how_works_title"] = "HOW IT WORKS",
                ["rbxm_how_works_1"] = "1. Add your .rbxm file(s) above.",
                ["rbxm_how_works_2"] = "2. In Studio, install RbxmImporter plugin and click ▶ Listen.",
                ["rbxm_how_works_3"] = "3. Click Send to Studio — the plugin auto-imports it.",

                // RSM Assistant View
                ["rsm_title"] = "ROBLOX STUDIO MANAGER (RSM)",
                ["rsm_sub"] = "Manage and install the RSM version of Roblox Studio",
                ["btn_rsm_install"] = "Install / Reinstall RSM",
                ["btn_rsm_repair"] = "Repair RSM",
                ["btn_rsm_open_folder"] = "Open Studio Folder",
                ["btn_rsm_delete"] = "Delete / Uninstall RSM",
                ["rsm_status_installed"] = "● RSM Installed (Active Priority):",
                ["rsm_status_not_installed"] = "○ RSM Not Installed (Using standard Roblox Studio)",
                ["rsm_alert_delete_title"] = "Confirm Uninstall RSM",
                ["rsm_alert_delete_msg"] = "Are you sure you want to completely uninstall RSM and remove its folders?\nThis action cannot be undone.",
                ["rsm_error_notice"] = "▲ An issue occurred with RSM. Try using 'Repair RSM' or use standard Roblox Studio.",

                // Studio Selector Modal
                ["modal_studio_title"] = "Detected Roblox Studio Installations",
                ["modal_studio_sub"] = "Select the Roblox Studio version you want to use for local test sessions:",
                ["modal_studio_empty"] = "No automatic installations found in default paths.",
                ["modal_studio_recommended"] = "RECOMMENDED",
                ["modal_studio_active"] = "✓ ACTIVE",
                ["modal_studio_close"] = "Close",

                // Tutorial View
                ["tut_title"] = "TUTORIAL & USER GUIDE",
                ["tut_sub"] = "Step-by-step guide to configure your server and connect to Roblox Studio sessions via tunnel",
                ["tut_s1_t"] = "Step 1: Open NepTunnel Application",
                ["tut_s1_d"] = "Launch NepTunnel. The app will automatically detect your Roblox Studio version (RSM, Bloxstrap, or Official).",
                ["tut_s2_t"] = "Step 2: Select 'Host Session'",
                ["tut_s2_d"] = "Click the purple 'HOST SESSION' button on the main menu to access server configuration.",
                ["tut_s3_t"] = "Step 3: Configure Tunnel Address & Port",
                ["tut_s3_d"] = "Enter your tunnel IP address or domain in 'Tunnel Address' and the local port in 'Server Local Port'.",
                ["tut_s4_t"] = "Step 4: Select Map File (Optional)",
                ["tut_s4_d"] = "If you want to load a specific place file (.rbxl / .rbxlx), use the 'Browse' button to select your map file.",
                ["tut_s5_t"] = "Step 5: Launch Roblox Studio Server",
                ["tut_s5_d"] = "Click 'Launch Server'. NepTunnel will start Roblox Studio in Local Test Server mode automatically.",
                ["tut_s6_t"] = "Step 6: Copy Address for Players",
                ["tut_s6_d"] = "Share your tunnel address (e.g. domain.com:55555) with your friends so they can join the game.",
                ["tut_s7_t"] = "Step 7: Join the Session (Joiner Mode)",
                ["tut_s7_d"] = "Guest players must select 'JOIN SESSION', paste the tunnel address, and click 'Connect & Launch'.",
                ["tut_s8_t"] = "Step 8: Verify Connection with Echo Test",
                ["tut_s8_d"] = "If you experience latency or issues, use the 'ECHO TEST' tool to verify direct packet transmission.",
                ["tut_s9_t"] = "Step 9: Import .rbxm Files into Studio",
                ["tut_s9_d"] = "Use the 'RBXM IMPORTER' to send models or scripts directly to your active Roblox Studio instance.",

                // Alerts & Confirmations
                ["alert_stop_host_title"] = "Stop Server",
                ["alert_stop_host_msg"] = "Are you sure you want to stop the hosting session?\nThis will close the local server and disconnect players.",
                ["alert_stop_host_btn"] = "Stop Server",

                ["alert_disc_title"] = "Disconnect Session",
                ["alert_disc_msg"] = "Are you sure you want to disconnect from the tunnel?",
                ["alert_disc_btn"] = "Disconnect",

                // Status Messages
                ["status_connected"] = "● Connected to session",
                ["status_disconnected"] = "○ Disconnected",

                // Alert Buttons
                ["alert_cancel"] = "Cancel"
            },
            ["es"] = new()
            {
                ["main_title"] = "¿Qué deseas hacer?",
                ["main_subtitle"] = "Hostear o unirse a una sesión mediante túnel",
                ["btn_host"] = "HOSTEAR SESIÓN",
                ["btn_join"] = "UNIRSE A SESIÓN",
                ["btn_echo"] = "PRUEBA DE ECO",
                ["btn_rbxm"] = "IMPORTADOR RBXM",
                ["btn_rsm_assistant"] = "ASISTENTE RSM",
                ["lbl_studio"] = "Studio:",
                ["lbl_tunnel_addr"] = "Dirección Túnel:",
                ["lbl_server_port"] = "Puerto Local Servidor:",
                ["lbl_uid"] = "ID de Usuario:",
                ["lbl_username"] = "Mi Usuario / Nick (Opcional):",
                ["lbl_proxy_port"] = "Puerto Proxy:",
                ["lbl_platform"] = "Plataforma:",
                ["lbl_bridge"] = "Bridge Studio:",
                ["browse"] = "Examinar",
                ["btn_copy_script"] = "Copiar Script",
                ["btn_inject_script"] = "Inyectar Script",
                ["back"] = "Atrás",
                ["test"] = "Probar",

                // Host Config View
                ["host_title"] = "HOSTEAR SESIÓN",
                ["host_sub"] = "Revisa la configuración, selecciona un mapa e inicia tu servidor",
                ["lbl_map_file"] = "Archivo de Mapa (Opcional)",
                ["btn_launch_server"] = "Iniciar Servidor",
                ["btn_tutorial"] = "Tutorial",

                // Host Running View
                ["host_console_title"] = "CONSOLA DEL SERVIDOR",
                ["btn_join_locally"] = "UNIRSE LOCALMENTE",
                ["btn_stop_back"] = "Detener y Volver",

                // Join Config View
                ["join_title"] = "UNIRSE A SESIÓN",
                ["join_sub"] = "Introduce la dirección del túnel del host",
                ["lbl_tunnel_input"] = "Dirección Túnel (host:puerto)",
                ["lbl_proxy_hint"] = "Hará proxy mediante 127.0.0.1:55555 → dirección remota",
                ["btn_connect_launch"] = "Conectar e Iniciar",

                // Join Running View
                ["join_console_title"] = "CONSOLA DE CONEXIÓN",
                ["btn_disc_back"] = "Desconectar y Volver",

                // Echo Test View
                ["echo_title"] = "PRUEBA DE ECO",
                ["echo_sub"] = "Verifica la conectividad del túnel antes de iniciar una sesión",
                ["lbl_studio_port_host"] = "Puerto Studio (host)",
                ["lbl_tunnel_addr_joiner"] = "Dirección Túnel (unidor)",
                ["btn_host_start_echo"] = "Host: Iniciar Eco",
                ["btn_host_stop_echo"] = "Host: Detener Eco",
                ["btn_join_run_echo"] = "Unidor: Ejecutar Eco",
                ["echo_how_to_use"] = "CÓMO USAR:\n  HOST:   Configura el puerto arriba y presiona \"Host: Iniciar Eco\"\n  UNIDOR: Introduce la dirección túnel arriba y presiona \"Unidor: Ejecutar Eco\"\n\n  Esta prueba envía paquetes directamente al túnel.\n  Puede demorar 3-5 segundos en responder el túnel.",

                // Rbxm Importer View
                ["rbxm_title"] = "IMPORTADOR RBXM",
                ["rbxm_sub"] = "Elige archivos .rbxm y envíalos a Studio mediante el plugin bridge",
                ["rbxm_empty"] = "No hay archivos guardados aún. Haz clic en + Añadir .rbxm para comenzar.",
                ["btn_add_rbxm"] = "+ Añadir .rbxm",
                ["btn_send_studio"] = "Enviar a Studio",
                ["rbxm_how_works_title"] = "CÓMO FUNCIONA",
                ["rbxm_how_works_1"] = "1. Añade tus archivos .rbxm arriba.",
                ["rbxm_how_works_2"] = "2. En Studio, instala el plugin RbxmImporter y haz clic en ▶ Escuchar.",
                ["rbxm_how_works_3"] = "3. Haz clic en Enviar a Studio: el plugin los importará automáticamente.",

                // RSM Assistant View
                ["rsm_title"] = "ASISTENTE ROBLOX STUDIO MANAGER (RSM)",
                ["rsm_sub"] = "Gestiona e instala la versión RSM de Roblox Studio",
                ["btn_rsm_install"] = "Instalar (Reinstalar RSM)",
                ["btn_rsm_repair"] = "Reparar RSM",
                ["btn_rsm_open_folder"] = "Abrir Carpeta de Roblox Studio",
                ["btn_rsm_delete"] = "Eliminar / Desinstalar RSM",
                ["rsm_status_installed"] = "● RSM Detectado (Prioridad Activa):",
                ["rsm_status_not_installed"] = "○ RSM No Instalado (Usando Roblox Studio estándar)",
                ["rsm_alert_delete_title"] = "Confirmar Desinstalación de RSM",
                ["rsm_alert_delete_msg"] = "¿Estás seguro de que deseas desinstalar RSM por completo y eliminar sus carpetas?\nEsta acción no se puede deshacer.",
                ["rsm_error_notice"] = "▲ Ocurrió un problema con RSM. Intenta usar 'Reparar RSM' o usa Roblox Studio estándar.",

                // Studio Selector Modal
                ["modal_studio_title"] = "Instalaciones de Roblox Studio Detectadas",
                ["modal_studio_sub"] = "Selecciona la versión de Roblox Studio que deseas usar para tus sesiones local test:",
                ["modal_studio_empty"] = "No se encontraron instalaciones automáticas en las rutas por defecto.",
                ["modal_studio_recommended"] = "RECOMENDADO",
                ["modal_studio_active"] = "✓ ACTIVO",
                ["modal_studio_close"] = "Cerrar",

                // Tutorial View
                ["tut_title"] = "TUTORIAL Y GUÍA DE USO",
                ["tut_sub"] = "Guía paso a paso para configurar tu servidor y conectarte a sesiones de Roblox Studio mediante el túnel",
                ["tut_s1_t"] = "Paso 1: Abrir la aplicación NepTunnel",
                ["tut_s1_d"] = "Ejecuta NepTunnel. La aplicación detectará automáticamente tu versión de Roblox Studio (RSM, Bloxstrap u Oficial).",
                ["tut_s2_t"] = "Paso 2: Seleccionar 'Hostear Sesión'",
                ["tut_s2_d"] = "Haz clic en el botón morado 'HOSTEAR SESIÓN' en el menú principal para acceder a la configuración del servidor.",
                ["tut_s3_t"] = "Paso 3: Configurar Dirección del Túnel y Puerto",
                ["tut_s3_d"] = "Introduce tu dirección IP o dominio del túnel en 'Dirección Túnel' y el puerto local en 'Puerto Local Servidor'.",
                ["tut_s4_t"] = "Paso 4: Seleccionar Archivo de Mapa (Opcional)",
                ["tut_s4_d"] = "Si deseas cargar un mapa específico (.rbxl / .rbxlx), usa el botón 'Buscar' para seleccionar tu archivo de juego.",
                ["tut_s5_t"] = "Paso 5: Iniciar el Servidor de Roblox Studio",
                ["tut_s5_d"] = "Haz clic en 'Iniciar Servidor'. NepTunnel iniciará Roblox Studio en modo Servidor Local Test automáticamente.",
                ["tut_s6_t"] = "Paso 6: Copiar Dirección para los Jugadores",
                ["tut_s6_d"] = "Comparte tu dirección del túnel (ej. dominio.com:55555) con tus amigos para que se unan a la partida.",
                ["tut_s7_t"] = "Paso 7: Unirse a la Sesión (Modo Unidor)",
                ["tut_s7_d"] = "Los jugadores invitados deben seleccionar 'UNIRSE A SESIÓN', pegar la dirección del túnel y hacer clic en 'Conectar e Iniciar'.",
                ["tut_s8_t"] = "Paso 8: Verificar la Conexión con Prueba de Eco",
                ["tut_s8_d"] = "Si experimentas latencia o problemas, usa la herramienta 'PRUEBA DE ECO' para probar el envío directo de paquetes.",
                ["tut_s9_t"] = "Paso 9: Importar Archivos .rbxm a Studio",
                ["tut_s9_d"] = "Usa el 'IMPORTADOR RBXM' para enviar modelos o scripts directamente a tu instancia activa de Roblox Studio.",

                // Alerts & Confirmations
                ["alert_stop_host_title"] = "Detener Servidor",
                ["alert_stop_host_msg"] = "¿Estás seguro de que deseas detener la sesión de hosting?\nEsto cerrará el servidor local y desconectará a los jugadores.",
                ["alert_stop_host_btn"] = "Detener Servidor",

                ["alert_disc_title"] = "Desconectar Sesión",
                ["alert_disc_msg"] = "¿Estás seguro de que deseas desconectarte del túnel?",
                ["alert_disc_btn"] = "Desconectar",

                // Status Messages
                ["status_connected"] = "● Conectado a la sesión",
                ["status_disconnected"] = "○ Desconectado",

                // Alert Buttons
                ["alert_cancel"] = "Cancelar"
            },
            ["pt"] = new()
            {
                ["main_title"] = "O que deseja fazer?",
                ["main_subtitle"] = "Hospedar ou entrar em uma sessão via túnel",
                ["btn_host"] = "HOSPEDAR SESSÃO",
                ["btn_join"] = "ENTRAR NA SESSÃO",
                ["btn_echo"] = "TESTE DE ECO",
                ["btn_rbxm"] = "IMPORTADOR RBXM",
                ["btn_rsm_assistant"] = "ASSISTENTE RSM",
                ["lbl_studio"] = "Studio:",
                ["lbl_tunnel_addr"] = "Endereço do Túnel:",
                ["lbl_server_port"] = "Porta Local do Servidor:",
                ["lbl_uid"] = "ID de Usuário:",
                ["lbl_username"] = "Meu Usuário / Nick (Opcional):",
                ["lbl_proxy_port"] = "Porta Proxy:",
                ["lbl_platform"] = "Plataforma:",
                ["lbl_bridge"] = "Bridge do Studio:",
                ["browse"] = "Navegar",
                ["btn_copy_script"] = "Copiar Script",
                ["btn_inject_script"] = "Injetar Script",
                ["back"] = "Voltar",
                ["test"] = "Testar",

                // Host Config View
                ["host_title"] = "HOSPEDAR SESSÃO",
                ["host_sub"] = "Revise a configuração, selecione o mapa e inicie seu servidor",
                ["lbl_map_file"] = "Arquivo de Mapa (Opcional)",
                ["btn_launch_server"] = "Iniciar Servidor",
                ["btn_tutorial"] = "Tutorial",

                // Host Running View
                ["host_console_title"] = "CONSOLE DO SERVIDOR",
                ["btn_join_locally"] = "ENTRAR LOCALMENTE",
                ["btn_stop_back"] = "Parar e Voltar",

                // Join Config View
                ["join_title"] = "ENTRAR NA SESSÃO",
                ["join_sub"] = "Insira o endereço do túnel do anfitrião",
                ["lbl_tunnel_input"] = "Endereço do Túnel (host:porta)",
                ["lbl_proxy_hint"] = "Fará proxy via 127.0.0.1:55555 → endereço remoto",
                ["btn_connect_launch"] = "Conectar e Iniciar",

                // Join Running View
                ["join_console_title"] = "CONSOLE DE CONEXÃO",
                ["btn_disc_back"] = "Desconectar e Voltar",

                // Echo Test View
                ["echo_title"] = "TESTE DE ECO",
                ["echo_sub"] = "Verifique a conectividade do túnel antes de iniciar uma sessão",
                ["lbl_studio_port_host"] = "Porta do Studio (host)",
                ["lbl_tunnel_addr_joiner"] = "Endereço do Túnel (participante)",
                ["btn_host_start_echo"] = "Host: Iniciar Eco",
                ["btn_host_stop_echo"] = "Host: Parar Eco",
                ["btn_join_run_echo"] = "Participante: Executar Eco",
                ["echo_how_to_use"] = "COMO USAR:\n  HOST:   Defina a porta acima e pressione \"Host: Iniciar Eco\"\n  PARTICIPANTE: Insira o endereço do túnel acima e pressione \"Participante: Executar Eco\"\n\n  Este teste envia pacotes diretamente para o túnel.",

                // Rbxm Importer View
                ["rbxm_title"] = "IMPORTADOR RBXM",
                ["rbxm_sub"] = "Escolha arquivos .rbxm e envie para o Studio via plugin bridge",
                ["rbxm_empty"] = "Nenhum arquivo salvo ainda. Clique em + Adicionar .rbxm para começar.",
                ["btn_add_rbxm"] = "+ Adicionar .rbxm",
                ["btn_send_studio"] = "Enviar para o Studio",
                ["rbxm_how_works_title"] = "COMO FUNCIONA",
                ["rbxm_how_works_1"] = "1. Adicione seus arquivos .rbxm acima.",
                ["rbxm_how_works_2"] = "2. No Studio, instale o plugin RbxmImporter e clique em ▶ Ouvir.",
                ["rbxm_how_works_3"] = "3. Clique em Enviar para o Studio — o plugin importará automaticamente.",

                // RSM Assistant View
                ["rsm_title"] = "ASSISTENTE ROBLOX STUDIO MANAGER (RSM)",
                ["rsm_sub"] = "Gerencie e instale a versão RSM do Roblox Studio",
                ["btn_rsm_install"] = "Instalar / Reinstalar RSM",
                ["btn_rsm_repair"] = "Reparar RSM",
                ["btn_rsm_open_folder"] = "Abrir Pasta do Studio",
                ["btn_rsm_delete"] = "Excluir / Desinstalar RSM",
                ["rsm_status_installed"] = "● RSM Instalado (Prioridade Ativa):",
                ["rsm_status_not_installed"] = "○ RSM Não Instalado (Usando Roblox Studio padrão)",
                ["rsm_alert_delete_title"] = "Confirmar Desinstalação do RSM",
                ["rsm_alert_delete_msg"] = "Tem certeza de que deseja desinstalar o RSM completamente e remover suas pastas?\nEsta ação não pode ser desfeita.",
                ["rsm_error_notice"] = "▲ Ocorreu um problema com o RSM. Tente usar 'Reparar RSM' ou use o Roblox Studio padrão.",

                // Studio Selector Modal
                ["modal_studio_title"] = "Instalações do Roblox Studio Detetadas",
                ["modal_studio_sub"] = "Selecione a versão do Roblox Studio que deseja usar para as suas sessões de teste local:",
                ["modal_studio_empty"] = "Nenhuma instalação automática foi encontrada nos caminhos padrão.",
                ["modal_studio_recommended"] = "RECOMENDADO",
                ["modal_studio_active"] = "✓ ATIVO",
                ["modal_studio_close"] = "Fechar",

                // Tutorial View
                ["tut_title"] = "TUTORIAL E GUIA DO USUÁRIO",
                ["tut_sub"] = "Guia passo a passo para configurar seu servidor e conectar-se a sessões do Roblox Studio via túnel",
                ["tut_s1_t"] = "Passo 1: Abrir a Aplicação NepTunnel",
                ["tut_s1_d"] = "Inicie o NepTunnel. O aplicativo detectará automaticamente sua versão do Roblox Studio.",
                ["tut_s2_t"] = "Passo 2: Selecionar 'Hospedar Sessão'",
                ["tut_s2_d"] = "Clique no botão roxo 'HOSPEDAR SESSÃO' no menu principal para acessar a configuração do servidor.",
                ["tut_s3_t"] = "Passo 3: Configurar Endereço e Porta do Túnel",
                ["tut_s3_d"] = "Insira o endereço IP do seu túnel ou domínio em 'Endereço do Túnel' e a porta local em 'Porta Local do Servidor'.",
                ["tut_s4_t"] = "Passo 4: Selecionar Arquivo de Mapa (Opcional)",
                ["tut_s4_d"] = "Se desejar carregar um arquivo de mapa específico (.rbxl / .rbxlx), use o botão 'Procurar' para selecionar seu arquivo.",
                ["tut_s5_t"] = "Passo 5: Iniciar Servidor do Roblox Studio",
                ["tut_s5_d"] = "Clique em 'Iniciar Servidor'. O NepTunnel iniciará o Roblox Studio no modo Servidor de Teste Local automaticamente.",
                ["tut_s6_t"] = "Passo 6: Copiar Endereço para os Jogadores",
                ["tut_s6_d"] = "Compartilhe seu endereço de túnel (ex: dominio.com:55555) com seus amigos para que eles entrem no jogo.",
                ["tut_s7_t"] = "Passo 7: Entrar na Sessão (Modo Participante)",
                ["tut_s7_d"] = "Os jogadores convidados devem selecionar 'ENTRAR NA SESSÃO', colar o endereço do túnel e clicar em 'Conectar e Iniciar'.",
                ["tut_s8_t"] = "Passo 8: Verificar Conexão com Teste de Eco",
                ["tut_s8_d"] = "Se você tiver problemas de latência ou conexão, use a ferramenta 'TESTE DE ECO' para testar a transmissão de pacotes.",
                ["tut_s9_t"] = "Passo 9: Importar Arquivos .rbxm para o Studio",
                ["tut_s9_d"] = "Use o 'IMPORTADOR RBXM' para enviar modelos ou scripts diretamente para sua instância ativa do Roblox Studio.",

                // Alerts & Confirmations
                ["alert_stop_host_title"] = "Parar Servidor",
                ["alert_stop_host_msg"] = "Tem certeza de que deseja parar a sessão de hospedagem?\nIsso fechará o servidor local e desconectará os jogadores.",
                ["alert_stop_host_btn"] = "Parar Servidor",

                ["alert_disc_title"] = "Desconectar Sessão",
                ["alert_disc_msg"] = "Tem certeza de que deseja se desconectar do túnel?",
                ["alert_disc_btn"] = "Desconectar",

                // Status Messages
                ["status_connected"] = "● Conectado à sessão",
                ["status_disconnected"] = "○ Desconectado",

                // Alert Buttons
                ["alert_cancel"] = "Cancelar"
            }
        };

        public static string Get(string key)
        {
            string lang = CurrentLanguage;
            if (!Translations.ContainsKey(lang))
                lang = "en";

            if (Translations[lang].TryGetValue(key, out var val))
                return val;

            if (Translations["en"].TryGetValue(key, out var fallbackVal))
                return fallbackVal;

            return key;
        }
    }
}
