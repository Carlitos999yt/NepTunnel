-- =========================================================================
--  NepTunnel - Dynamic Player Name Synchronization & Leaderboard Overrider
--  Place this script in ServerScriptService inside your Roblox Place (.rbxl)
-- =========================================================================

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")

-- Enable HTTP Requests automatically in Roblox Studio local mode
pcall(function()
    HttpService.HttpEnabled = true
end)

local BRIDGE_URL = "http://127.0.0.1:7878/identity"

-- Helper function to fetch configured identity from NepTunnel Local Bridge
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

-- TÉCNICA #1: Apply DisplayName to Character Humanoid
local function applyHumanoidName(player, customName)
    local function onCharacterAdded(character)
        local humanoid = character:WaitForChild("Humanoid", 10)
        if humanoid then
            pcall(function()
                humanoid.DisplayName = customName
            end)
        end
    end

    if player.Character then
        onCharacterAdded(player.Character)
    end
    player.CharacterAdded:Connect(onCharacterAdded)
end

-- TÉCNICA #3: Create Custom Player List Leaderboard UI in PlayerGui
local function createCustomLeaderboard(player, customName)
    local playerGui = player:WaitForChild("PlayerGui", 10)
    if not playerGui then return end

    -- Disable Roblox Default PlayerList
    pcall(function()
        game:GetService("StarterGui"):SetCoreGuiEnabled(Enum.CoreGuiType.PlayerList, false)
    end)

    local existing = playerGui:FindFirstChild("NepCustomLeaderboard")
    if existing then existing:Destroy() end

    local screenGui = Instance.new("ScreenGui")
    screenGui.Name = "NepCustomLeaderboard"
    screenGui.ResetOnSpawn = false

    local frame = Instance.new("Frame")
    frame.Size = UDim2.new(0, 180, 0, 100)
    frame.Position = UDim2.new(1, -190, 0, 10)
    frame.BackgroundColor3 = Color3.fromRGB(15, 15, 20)
    frame.BackgroundTransparency = 0.2
    frame.BorderSizePixel = 0
    frame.Parent = screenGui

    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 8)
    corner.Parent = frame

    local header = Instance.new("TextLabel")
    header.Size = UDim2.new(1, 0, 0, 30)
    header.BackgroundTransparency = 1
    header.Text = "Personas"
    header.TextColor3 = Color3.fromRGB(200, 200, 200)
    header.Font = Enum.Font.SourceSansBold
    header.TextSize = 14
    header.Parent = frame

    local playerRow = Instance.new("TextLabel")
    playerRow.Size = UDim2.new(1, -20, 0, 25)
    playerRow.Position = UDim2.new(0, 10, 0, 35)
    playerRow.BackgroundTransparency = 1
    playerRow.Text = "● " .. customName
    playerRow.TextColor3 = Color3.fromRGB(255, 255, 255)
    playerRow.Font = Enum.Font.SourceSansSemibold
    playerRow.TextSize = 16
    playerRow.TextXAlignment = Enum.TextXAlignment.Left
    playerRow.Parent = frame

    screenGui.Parent = playerGui
end

-- Process All Players
local function handlePlayer(player)
    task.spawn(function()
        local customName = fetchNepIdentity() or player.Name
        applyHumanoidName(player, customName)
        createCustomLeaderboard(player, customName)
    end)
end

Players.PlayerAdded:Connect(handlePlayer)
for _, player in ipairs(Players:GetPlayers()) do
    handlePlayer(player)
end

print("[NepTunnel] NepNameSyncScript (Técnica 1 + 3) loaded successfully!")
