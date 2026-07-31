-- =========================================================================
--  NepTunnel - Server Name Synchronization Script
--  Colocar este Script en: ServerScriptService
-- =========================================================================

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")

-- Activar solicitudes HTTP automáticamente
pcall(function()
    HttpService.HttpEnabled = true
end)

local BRIDGE_URL = "http://127.0.0.1:7878/identity"

local function fetchNepIdentity()
    local success, responseText = pcall(function()
        return HttpService:GetAsync(BRIDGE_URL)
    end)

    if success and responseText then
        local decodeSuccess, data = pcall(function()
            return HttpService:JSONDecode(responseText)
        end)

        if decodeSuccess and data and data.name and data.name ~= "" then
            return data.name
        end
    end
    return nil
end

local function onPlayerAdded(player)
    task.spawn(function()
        local customName = fetchNepIdentity()
        if customName and customName ~= "" then
            pcall(function()
                player.DisplayName = customName
            end)

            -- Guardar valor para que el cliente lo lea
            local val = player:FindFirstChild("NepCustomName")
            if not val then
                val = Instance.new("StringValue")
                val.Name = "NepCustomName"
                val.Parent = player
            end
            val.Value = customName
        end

        local function onCharacterAdded(character)
            local humanoid = character:WaitForChild("Humanoid", 10)
            if humanoid and customName then
                pcall(function()
                    humanoid.DisplayName = customName
                end)
            end
        end

        if player.Character then
            onCharacterAdded(player.Character)
        end
        player.CharacterAdded:Connect(onCharacterAdded)
    end)
end

Players.PlayerAdded:Connect(onPlayerAdded)
for _, p in ipairs(Players:GetPlayers()) do
    onPlayerAdded(p)
end

print("[NepTunnel] Server Name Sync initialized!")
