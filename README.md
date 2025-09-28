# BigFix Universal Remote QnA

A cross-platform GUI application for executing BigFix QnA (Relevance) queries remotely via SSH on Windows, Linux, and macOS systems.

## ✨ Features

- **Cross-Platform Support** - Execute QnA queries on Windows, Linux, and macOS remotely
- **SSH Connectivity** - Secure remote connections with encrypted password storage
- **Connection Profiles** - Save and manage multiple server configurations
- **Query Management** - Save, load, and maintain history of recent queries
- **Real-time Results** - View query output and error messages instantly
- **Path Detection** - Automatic QnA executable path detection for different OS types

## 🖥️ System Requirements

- **Local Machine**: Python 3+ (for development) or standalone executable
- **Target Machines**: BigFix Client installed with SSH access enabled
- **Network**: SSH connectivity (port 22) to target machines

## 🚀 Quick Start

### Using the Executable
1. Download `BigFixUniversalRemoteQnA.exe`
2. Run the application
3. Configure connection settings
4. Connect and execute queries

### Using Python Source
```bash
# Install pipenv if not already installed
pip install pipenv

# Install dependencies from Pipfile
pipenv install --dev

# Activate virtual environment and run application
pipenv run python main.py

# Alternative: Activate shell then run
pipenv shell
python main.py
```
## 📋 Usage

### 1. Connection Setup
- **Host/IP**: hostname/Target machine IP
- **Port**: SSH port (default: 22)
- **Username/Password**: SSH credentials
- **Target OS**: Select Windows/Linux/Mac
- **QnA Path**: Auto-populated based on OS

### 2. Save Connection Profiles
- Click "Save Profile" to store connection settings
- Profiles are saved locally and can be reused
- Passwords are encrypted when "Save passwords" is enabled

### 3. Execute Queries
- Enter Relevance query in the text area
- Click "Execute Query" to run remotely
- View results in the output section
- Recent queries are automatically saved

## 📁 Default QnA Paths

| OS | Default Path |
|----|--------------|
| **Windows** | `C:\Program Files (x86)\BigFix Enterprise\BES Client\QnA.exe` |
| **Linux** | `/opt/BESClient/bin/qna` |
| **macOS** | `/Library/BESAgent/BESAgent.app/Contents/MacOS/QnA` |

## 💡 Example Queries

```relevance
name of operating system
version of client
number of processors
```

## 🔧 Configuration

- **Profiles**: Saved to `~/.bigfix_profiles.json`
- **Settings**: Saved to `~/.bigfix_universal_qna_config.json`
- **Window**: Size and position automatically saved


## 🔒 Security

- SSH connections use industry-standard encryption
- Passwords are encrypted using Fernet (AES 128) when stored
- No credentials are transmitted in plain text
- Connection profiles are stored locally only

## ⚠️ Prerequisites

### Target Machine Requirements
- BigFix Client/Agent installed and running
- SSH server enabled and accessible
- QnA executable available at the specified path
- Valid SSH user account with appropriate permissions

### Network Requirements
- SSH port (22) open between local and target machines
- Network connectivity to target systems

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Connection Failed** | Verify SSH service, credentials, and network connectivity |
| **QnA Not Found** | Check BigFix client installation and verify QnA path |
| **Permission Denied** | Ensure SSH user has execute permissions for QnA |
| **Query Timeout** | Complex queries may need more time; check target system resources |


## 🤝 Contributing

1. Fork/Clone the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📚 Resources

- [Relevance Language Guide](https://developer.bigfix.com/relevance/)
- [SSH Configuration Guide](https://www.ssh.com/academy/ssh/config)


## Troubleshooting: Install and Enable OpenSSH Server on Windows

### Install OpenSSH Server

Run PowerShell as **Administrator**:

```powershell
Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH*'
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
```

### Start Service and Set to Auto-Start

```powershell
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
```

### Allow SSH Through Windows Firewall (Port 22)

> **Tip:** This rule is often auto-created; add if missing.

```powershell
New-NetFirewallRule -Name 'sshd' -DisplayName 'OpenSSH Server (sshd)' `
 -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

### Verify Service and Connectivity

```powershell
Get-Service sshd
Test-NetConnection -ComputerName localhost -Port 22
```

### (Optional) Enable Key-Based Authentication

Edit the SSH server config:

```powershell
notepad 'C:\ProgramData\ssh\sshd_config'
```

After changes, restart the service:

```powershell
Restart-Service sshd
```

### Uninstall (If Needed)

```powershell
Remove-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
```

### Notes

- On Windows 10/11: **Settings → Apps → Optional features → Add a feature → “OpenSSH Server”**.
- Ensure the account (local/domain) and credentials/keys used are valid on the target machine.
