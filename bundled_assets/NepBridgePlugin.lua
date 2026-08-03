-- =========================================================================
--  NepTunnel - Roblox Studio Auto-Bridge & NameSync Plugin
--  Auto-installed by NepTunnel into %LOCALAPPDATA%\Roblox\Plugins
-- =========================================================================

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ServerScriptService = game:GetService("ServerScriptService")
local StarterGui = game:GetService("StarterGui")

-- 1. Enable HttpService from Plugin Security Level
pcall(function()
    HttpService.HttpEnabled = true
end)

-- 2. Plugin Direct Name Sync Handler (Bypasses place security restrictions)
local function applyCustomNameDirectly(player, customName)
    if not customName or customName == "" or customName == "Player" then return end
    pcall(function() player.DisplayName = customName end)
    local val = player:FindFirstChild("NepCustomName")
    if not val then
        val = Instance.new("StringValue")
        val.Name = "NepCustomName"
        val.Parent = player
    end
    val.Value = customName
    local function onCharacter(char)
        local hum = char:WaitForChild("Humanoid", 10)
        if hum then pcall(function() hum.DisplayName = customName end) end
    end
    if player.Character then onCharacter(player.Character) end
    player.CharacterAdded:Connect(onCharacter)
end

local function pluginFetchIdentity(role)
    local url = "http://127.0.0.1:7878/identity?role=" .. tostring(role)
    local success, res = pcall(function() return HttpService:GetAsync(url) end)
    if success and res then
        local decSuccess, data = pcall(function() return HttpService:JSONDecode(res) end)
        if decSuccess and data and data.name and data.name ~= "" and data.name ~= "Player" then
            return data.name
        end
    end
    return nil
end

local function pluginProcessPlayer(player)
    task.spawn(function()
        local pName = player.Name
        if string.find(pName, "NepNick_") then
            local cleanName = string.gsub(pName, "NepNick_", "")
            cleanName = string.gsub(cleanName, "_", " ")
            if cleanName ~= "" and cleanName ~= "Player" then
                applyCustomNameDirectly(player, cleanName)
                return
            end
        end

        for attempt = 1, 15 do
            local isFirstPlayer = (player.Name == "Player1" or #Players:GetPlayers() <= 1)
            local role = isFirstPlayer and "host" or "client"
            local name = pluginFetchIdentity(role)
            if name and name ~= "" and name ~= "Player" then
                applyCustomNameDirectly(player, name)
                break
            end
            task.wait(1)
        end
    end)
end

Players.PlayerAdded:Connect(pluginProcessPlayer)
for _, p in ipairs(Players:GetPlayers()) do
    pluginProcessPlayer(p)
end

-- 3. Inject NepServerNameSync into ServerScriptService (Preserves user edits unless force=true)
local function ensureServerNameSync(force)
    local s = ServerScriptService:FindFirstChild("NepServerNameSync")
    if s and not force then return end -- Respect existing user edits!
    if not s then
        s = Instance.new("Script")
        s.Name = "NepServerNameSync"
        s.Parent = ServerScriptService
    end
    s.Source = [[
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")

pcall(function() HttpService.HttpEnabled = true end)

local function applyCustomName(player, customName)
    if not customName or customName == "" or customName == "Player" then return end
    pcall(function() player.DisplayName = customName end)
    local val = player:FindFirstChild("NepCustomName")
    if not val then
        val = Instance.new("StringValue")
        val.Name = "NepCustomName"
        val.Parent = player
    end
    val.Value = customName
    local function onCharacter(char)
        local hum = char:WaitForChild("Humanoid", 10)
        if hum then pcall(function() hum.DisplayName = customName end) end
    end
    if player.Character then onCharacter(player.Character) end
    player.CharacterAdded:Connect(onCharacter)
end

local function fetchLocalIdentity()
    local url = "http://127.0.0.1:7878/identity"
    local success, res = pcall(function() return HttpService:GetAsync(url) end)
    if success and res then
        local decSuccess, data = pcall(function() return HttpService:JSONDecode(res) end)
        if decSuccess and data and data.name and data.name ~= "" and data.name ~= "Player" then
            return data.name
        end
    end
    return nil
end

local function processPlayer(player)
    task.spawn(function()
        local pName = player.Name
        if string.find(pName, "NepNick_") then
            local cleanName = string.gsub(pName, "NepNick_", "")
            cleanName = string.gsub(cleanName, "_", " ")
            if cleanName ~= "" and cleanName ~= "Player" then
                applyCustomName(player, cleanName)
                return
            end
        end

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
for _, p in ipairs(Players:GetPlayers()) do processPlayer(p) end
]]
end

-- 4. Inject NepClientLeaderboard into StarterGui (Preserves user edits unless force=true)
local function ensureClientLeaderboard(force)
    local ls = StarterGui:FindFirstChild("NepClientLeaderboard")
    if ls and not force then return end -- Respect existing user edits!
    if not ls then
        ls = Instance.new("LocalScript")
        ls.Name = "NepClientLeaderboard"
        ls.Parent = StarterGui
    end
    ls.Source = [[
local Players = game:GetService("Players")
local StarterGui = game:GetService("StarterGui")
local ContextActionService = game:GetService("ContextActionService")
local localPlayer = Players.LocalPlayer

task.spawn(function()
    while true do
        pcall(function() StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.PlayerList, false) end)
        task.wait(0.5)
    end
end)

local function buildLeaderboard()
    local playerGui = localPlayer:WaitForChild("PlayerGui")
    local existing = playerGui:FindFirstChild("NepCustomLeaderboard")
    if existing then existing:Destroy() end

    local screenGui = Instance.new("ScreenGui")
    screenGui.Name = "NepCustomLeaderboard"
    screenGui.ResetOnSpawn = false

    local frame = Instance.new("Frame")
    frame.Name = "LeaderboardFrame"
    frame.Size = UDim2.new(0, 220, 0, 110)
    frame.Position = UDim2.new(1, -230, 0, 10)
    frame.BackgroundColor3 = Color3.fromRGB(15, 15, 20)
    frame.BackgroundTransparency = 0.25
    frame.BorderSizePixel = 0
    frame.Parent = screenGui

    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 8)
    corner.Parent = frame

    local headerName = Instance.new("TextLabel")
    headerName.Size = UDim2.new(0.65, 0, 0, 30)
    headerName.Position = UDim2.new(0, 10, 0, 2)
    headerName.BackgroundTransparency = 1
    headerName.Text = "Personas"
    headerName.TextColor3 = Color3.fromRGB(200, 200, 200)
    headerName.Font = Enum.Font.SourceSansBold
    headerName.TextSize = 14
    headerName.TextXAlignment = Enum.TextXAlignment.Left
    headerName.Parent = frame

    local headerMin = Instance.new("TextLabel")
    headerMin.Size = UDim2.new(0.35, -10, 0, 30)
    headerMin.Position = UDim2.new(0.65, 0, 0, 2)
    headerMin.BackgroundTransparency = 1
    headerMin.Text = "Minutes"
    headerMin.TextColor3 = Color3.fromRGB(200, 200, 200)
    headerMin.Font = Enum.Font.SourceSansBold
    headerMin.TextSize = 14
    headerMin.TextXAlignment = Enum.TextXAlignment.Right
    headerMin.Parent = frame

    local div = Instance.new("Frame")
    div.Size = UDim2.new(1, -20, 0, 1)
    div.Position = UDim2.new(0, 10, 0, 32)
    div.BackgroundColor3 = Color3.fromRGB(60, 60, 80)
    div.BorderSizePixel = 0
    div.Parent = frame

    local container = Instance.new("Frame")
    container.Name = "RowsContainer"
    container.Size = UDim2.new(1, -20, 1, -36)
    container.Position = UDim2.new(0, 10, 0, 34)
    container.BackgroundTransparency = 1
    container.Parent = frame

    local function updateList()
        container:ClearAllChildren()
        local yOffset = 0
        local nameCounts = {}

        for _, plr in ipairs(Players:GetPlayers()) do
            local row = Instance.new("Frame")
            row.Size = UDim2.new(1, 0, 0, 24)
            row.Position = UDim2.new(0, 0, 0, yOffset)
            row.BackgroundTransparency = 1
            row.Parent = container

            local customVal = plr:FindFirstChild("NepCustomName")
            local rawName = (customVal and customVal.Value ~= "") and customVal.Value or plr.DisplayName
            
            nameCounts[rawName] = (nameCounts[rawName] or 0) + 1
            local finalDisplay = rawName
            if nameCounts[rawName] > 1 then
                finalDisplay = rawName .. " (" .. tostring(nameCounts[rawName]) .. ")"
            end

            local nameLbl = Instance.new("TextLabel")
            nameLbl.Size = UDim2.new(0.65, 0, 1, 0)
            nameLbl.BackgroundTransparency = 1
            nameLbl.Text = "● " .. finalDisplay
            nameLbl.TextColor3 = Color3.fromRGB(255, 255, 255)
            nameLbl.Font = Enum.Font.SourceSansSemibold
            nameLbl.TextSize = 15
            nameLbl.TextXAlignment = Enum.TextXAlignment.Left
            nameLbl.Parent = row

            local valLbl = Instance.new("TextLabel")
            valLbl.Size = UDim2.new(0.35, 0, 1, 0)
            valLbl.Position = UDim2.new(0.65, 0, 0, 0)
            valLbl.BackgroundTransparency = 1
            valLbl.Text = "0"
            valLbl.TextColor3 = Color3.fromRGB(220, 220, 220)
            valLbl.Font = Enum.Font.SourceSans
            valLbl.TextSize = 15
            valLbl.TextXAlignment = Enum.TextXAlignment.Right
            valLbl.Parent = row

            local function hookLeaderstats()
                local ls = plr:FindFirstChild("leaderstats") or plr:WaitForChild("leaderstats", 5)
                if ls then
                    local mins = ls:FindFirstChild("Minutes") or ls:FindFirstChildOfClass("IntValue") or ls:FindFirstChildOfClass("NumberValue")
                    if mins then
                        valLbl.Text = tostring(mins.Value)
                        mins.Changed:Connect(function(v) valLbl.Text = tostring(v) end)
                    end
                end
            end
            task.spawn(hookLeaderstats)

            if customVal then customVal.Changed:Connect(updateList) end
            yOffset = yOffset + 26
        end
        frame.Size = UDim2.new(0, 220, 0, math.max(65, 42 + yOffset))
    end

    Players.PlayerAdded:Connect(updateList)
    Players.PlayerRemoving:Connect(updateList)
    updateList()

    local function handleTabAction(actionName, inputState, inputObject)
        if inputState == Enum.UserInputState.Begin then frame.Visible = not frame.Visible end
        return Enum.ContextActionResult.Sink
    end

    pcall(function() ContextActionService:UnbindAction("NepToggleCustomTab") end)
    ContextActionService:BindActionAtPriority("NepToggleCustomTab", handleTabAction, false, Enum.ContextActionPriority.High.Value + 2000, Enum.KeyCode.Tab)
    screenGui.Parent = playerGui
end

task.spawn(buildLeaderboard)
]]
end

-- Check bridge for import signals
task.spawn(function()
    for attempt = 1, 10 do
        local url = "http://127.0.0.1:7878/identity?role=host"
        local success, res = pcall(function() return HttpService:GetAsync(url) end)
        if success and res then
            local decSuccess, data = pcall(function() return HttpService:JSONDecode(res) end)
            if decSuccess and data then
                local isForce = (data.force_import == true)
                pcall(function() ensureServerNameSync(isForce) end)
                pcall(function() ensureClientLeaderboard(isForce) end)
                break
            end
        end
        task.wait(1)
    end
end)
