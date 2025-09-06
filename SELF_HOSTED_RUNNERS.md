# Self-Hosted Runner Setup Guide

This guide explains how to set up and configure self-hosted GitHub Actions runners for the CCC Clock Demonstration System repository.

## Overview

Self-hosted runners provide several advantages for this repository:
- **Better performance** for compute-intensive tasks (animation generation, testing)
- **Custom environment control** for specialized dependencies
- **Cost efficiency** for frequent builds
- **Hardware-specific optimizations** for scientific computing workloads

## Prerequisites

- A machine running Linux, macOS, or Windows
- At least 4GB RAM and 10GB free disk space
- Network access to GitHub.com
- Administrative/sudo privileges for installing dependencies
- Git installed on the system

## Quick Setup

### 1. Create Runner Directory
```bash
mkdir actions-runner && cd actions-runner
```

### 2. Download Runner Package

**For Linux x64:**
```bash
curl -o actions-runner-linux-x64-2.328.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.328.0/actions-runner-linux-x64-2.328.0.tar.gz
```

**For macOS x64:**
```bash
curl -o actions-runner-osx-x64-2.328.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.328.0/actions-runner-osx-x64-2.328.0.tar.gz
```

**For Windows x64:**
```powershell
Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.328.0/actions-runner-win-x64-2.328.0.zip -OutFile actions-runner-win-x64-2.328.0.zip
```

### 3. Validate Package (Optional but Recommended)

**Linux:**
```bash
echo "3b21bb9b7b95c1b73b3e5d59295d3e0d10c7494d9d26ca74ed55b7f10fa15e6c  actions-runner-linux-x64-2.328.0.tar.gz" | sha256sum -c
```

**macOS:**
```bash
echo "90c32dc6f292855339563148f3859dc5d402f237ecdf57010c841df3c8d12cc8  actions-runner-osx-x64-2.328.0.tar.gz" | shasum -a 256 -c
```

### 4. Extract Package

**Linux/macOS:**
```bash
tar xzf ./actions-runner-*.tar.gz
```

**Windows:**
```powershell
Expand-Archive -Path actions-runner-win-x64-2.328.0.zip -DestinationPath .
```

### 5. Configure Runner

```bash
./config.sh --url https://github.com/Tnsr-Q/ccc_clock --token <YOUR_TOKEN>
```

**Note:** Replace `<YOUR_TOKEN>` with a registration token from your repository's Settings > Actions > Runners page.

### 6. Install Dependencies

**For CCC Clock repository, install these dependencies:**

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv ffmpeg build-essential
```

**macOS:**
```bash
brew install python ffmpeg
```

**Windows:**
- Install Python 3.9+ from python.org
- Install FFmpeg from https://ffmpeg.org/download.html
- Add both to your PATH

### 7. Start Runner

**Interactive mode (for testing):**
```bash
./run.sh
```

**As a service (recommended for production):**

**Linux:**
```bash
sudo ./svc.sh install
sudo ./svc.sh start
```

**macOS:**
```bash
./svc.sh install
./svc.sh start
```

**Windows (as Administrator):**
```powershell
.\svc.sh install
.\svc.sh start
```

## Using Self-Hosted Runners

### Automatic Trigger

The repository includes smart logic to automatically use self-hosted runners:

1. **Manual trigger**: Use GitHub's "Actions" tab and run "Self-Hosted CI" workflow
2. **Commit message**: Include `[self-hosted]` in your commit message
3. **Workflow dispatch**: Use the workflow dispatch button with self-hosted option enabled

### Manual Workflow Configuration

To always use self-hosted runners, modify workflow files to use:
```yaml
runs-on: self-hosted
```

### Hybrid Configuration

The repository supports hybrid configurations that fall back to GitHub-hosted runners:
```yaml
runs-on: ${{ contains(github.event.head_commit.message, '[self-hosted]') && 'self-hosted' || 'ubuntu-latest' }}
```

## Runner Maintenance

### Updating Runner

```bash
cd actions-runner
./config.sh remove --token <REMOVE_TOKEN>
# Download and extract new version
./config.sh --url https://github.com/Tnsr-Q/ccc_clock --token <NEW_TOKEN>
```

### Monitoring Runner Status

- Check runner status in GitHub repository Settings > Actions > Runners
- Monitor system resources during builds
- Check runner logs: `_diag` folder in runner directory

### Troubleshooting

**Runner not appearing online:**
- Check network connectivity to GitHub
- Verify token is valid and has correct permissions
- Check firewall settings (runner needs outbound HTTPS access)

**Build failures:**
- Ensure all dependencies are installed (Python, FFmpeg, etc.)
- Check disk space (animations can be large)
- Verify Python virtual environment is clean

**Permission issues:**
- Ensure runner has write access to work directory
- Check sudo/admin privileges for dependency installation

## Security Considerations

- **Run on trusted networks**: Self-hosted runners execute arbitrary code
- **Isolate runner environment**: Consider using containers or VMs
- **Regular updates**: Keep runner software and OS updated
- **Monitor resource usage**: Set up alerts for unusual activity
- **Limit repository access**: Only use with trusted repositories

## Performance Optimization

### For CCC Clock Repository

**Recommended system specs:**
- **CPU**: 4+ cores (for parallel testing)
- **RAM**: 8GB+ (for animation generation)
- **Storage**: SSD with 20GB+ free space
- **Network**: Stable broadband connection

**Performance tips:**
- Use SSD storage for faster I/O
- Ensure adequate cooling for sustained workloads
- Consider dedicated runners for compute-intensive tasks
- Monitor memory usage during animation generation

## Integration with Repository

The CCC Clock repository includes several workflows optimized for self-hosted runners:

- **`self-hosted-ci.yml`**: Main testing and validation pipeline
- **Smart fallback**: Automatically uses GitHub-hosted runners if self-hosted unavailable
- **Artifact optimization**: Efficient handling of large animation files
- **Multi-platform support**: Works with Linux, macOS, and Windows runners

## Getting Help

- **GitHub Documentation**: [About self-hosted runners](https://docs.github.com/en/actions/hosting-your-own-runners/about-self-hosted-runners)
- **Repository Issues**: Open an issue in this repository for CCC Clock-specific problems
- **Community Support**: GitHub Community Forums for general runner questions

## Next Steps

1. Set up your first runner using the quick setup guide above
2. Test with a simple workflow dispatch
3. Monitor performance and adjust system resources as needed
4. Consider setting up multiple runners for high availability
5. Explore advanced configurations for your specific use case