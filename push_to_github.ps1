param(
    [Parameter(Mandatory=$false)]
    [string]$RepoName = "Doraemon_Shinchan_character_recognition_model",
    [Parameter(Mandatory=$false)]
    [string]$Token = ""
)

if ([string]::IsNullOrWhiteSpace($Token)) {
    $Token = Read-Host "Please enter your GitHub Personal Access Token (classic, with 'repo' scope)"
}

if ([string]::IsNullOrWhiteSpace($Token)) {
    Write-Host "No token provided. Exiting." -ForegroundColor Red
    exit 1
}

# Create the repository via GitHub API
Write-Host "Creating repository '$RepoName' on GitHub..." -ForegroundColor Cyan
$headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
}

$body = @{
    "name" = $RepoName
    "private" = $false
    "description" = "Doraemon and Shin-chan Character Recognition Deep Learning Model"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body -ErrorAction Stop
    $cloneUrl = $response.clone_url
    Write-Host "Successfully created repository at $cloneUrl" -ForegroundColor Green
} catch {
    Write-Host "Failed to create repository. It might already exist or the token is invalid." -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

# Push to the repository
Write-Host "Adding remote and pushing code..." -ForegroundColor Cyan
git remote remove origin 2>$null
git remote add origin $cloneUrl
git branch -M main

# We use the token in the URL for authentication during the push
$authUrl = $cloneUrl -replace "https://", "https://$Token@"
git push -u $authUrl main

Write-Host "Code successfully pushed to GitHub!" -ForegroundColor Green
Write-Host "You can now proceed to the deployment phase on Render and Vercel." -ForegroundColor Yellow
