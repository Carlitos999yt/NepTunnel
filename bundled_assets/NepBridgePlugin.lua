-- =========================================================================
--  NepTunnel - Roblox Studio Auto-Import Plugin
--  Auto-installed by NepTunnel into %LOCALAPPDATA%\Roblox\Plugins
-- =========================================================================

local HttpService = game:GetService("HttpService")
local ServerScriptService = game:GetService("ServerScriptService")

pcall(function()
    HttpService.HttpEnabled = true
end)

local POLL_URL = "http://127.0.0.1:7878/poll"

task.spawn(function()
    while true do
        task.wait(2)
        local success, responseText = pcall(function()
            return HttpService:GetAsync(POLL_URL)
        end)

        if success and responseText then
            local decSuccess, data = pcall(function()
                return HttpService:JSONDecode(responseText)
            end)

            if decSuccess and data and data.status == "ready" and data.name then
                -- Import model/script package
                local existing = ServerScriptService:FindFirstChild("NepNameSyncScript")
                if not existing then
                    print("[NepTunnel Plugin] Staged package detected: " .. tostring(data.name))
                end
            end
        end
    end
end)
