-- =========================================================================
--  NepTunnel - Server Name Synchronization & Remote Identity Sync
--  Colocar este Script en: ServerScriptService
-- =========================================================================

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")

pcall(function()
    HttpService.HttpEnabled = true
end)

local function applyCustomName(player, customName)
    if not customName or customName == "" or customName == "Player" then return end
    
    pcall(function()
        player.DisplayName = customName
    end)

    local val = player:FindFirstChild("NepCustomName")
    if not val then
        val = Instance.new("StringValue")
        val.Name = "NepCustomName"
        val.Parent = player
    end
    val.Value = customName

    local function onCharacter(char)
        local hum = char:WaitForChild("Humanoid", 10)
        if hum then
            pcall(function()
                hum.DisplayName = customName
            end)
        end
    end

    if player.Character then
        onCharacter(player.Character)
    end
    player.CharacterAdded:Connect(onCharacter)
end

local function fetchLocalIdentity()
    local url = "http://127.0.0.1:7878/identity"
    local success, res = pcall(function()
        return HttpService:GetAsync(url)
    end)
    if success and res then
        local decSuccess, data = pcall(function()
            return HttpService:JSONDecode(res)
        end)
        if decSuccess and data and data.name and data.name ~= "" and data.name ~= "Player" then
            return data.name
        end
    end
    return nil
end

local function processPlayer(player)
    task.spawn(function()
        -- 1. Check if player instance name contains NepNick_ (Passed via -instanceId from client)
        local pName = player.Name
        if string.find(pName, "NepNick_") then
            local cleanName = string.gsub(pName, "NepNick_", "")
            cleanName = string.gsub(cleanName, "_", " ")
            if cleanName ~= "" and cleanName ~= "Player" then
                applyCustomName(player, cleanName)
                return
            end
        end

        -- 2. If Host (Player1 / first player), fetch from local NepTunnel HTTP server
        for attempt = 1, 15 do
            local isFirstPlayer = (player.Name == "Player1" or #Players:GetPlayers() <= 1)
            if isFirstPlayer then
                local name = fetchLocalIdentity()
                if name and name ~= "" and name ~= "Player" then
                    applyCustomName(player, name)
                    break
                end
            end
            task.wait(1)
        end
    end)
end

Players.PlayerAdded:Connect(processPlayer)
for _, player in ipairs(Players:GetPlayers()) do
    processPlayer(player)
end
