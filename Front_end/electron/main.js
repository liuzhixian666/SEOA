const { app, BrowserWindow, Menu, shell } = require('electron')
const path = require('path')
const { spawn } = require('child_process')
const fs = require('fs')

let mainWindow = null
let pythonProcess = null

const isDev = !app.isPackaged

function getPythonPath() {
  if (isDev) {
    return 'python'
  }
  const resourcePath = process.resourcesPath
  const pythonPath = path.join(resourcePath, 'python', 'python.exe')
  if (fs.existsSync(pythonPath)) {
    return pythonPath
  }
  return 'python'
}

function getBackendPath() {
  if (isDev) {
    return path.join(__dirname, '..', '..', 'Back_end', 'main.py')
  }
  const appPath = app.getAppPath()
  const exeDir = path.dirname(appPath)
  return path.join(exeDir, 'Back_end', 'main.py')
}

function startPythonBackend() {
  const pythonPath = getPythonPath()
  const backendPath = getBackendPath()
  
  console.log('Starting Python backend...')
  console.log('Python path:', pythonPath)
  console.log('Backend path:', backendPath)

  const backendDir = path.dirname(backendPath)
  
  pythonProcess = spawn(pythonPath, [backendPath], {
    cwd: backendDir,
    env: { ...process.env },
    stdio: ['ignore', 'pipe', 'pipe']
  })

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Backend stdout: ${data}`)
  })

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Backend stderr: ${data}`)
  })

  pythonProcess.on('error', (err) => {
    console.error('Failed to start Python backend:', err)
  })

  pythonProcess.on('close', (code) => {
    console.log(`Python backend exited with code ${code}`)
    pythonProcess = null
  })

  return new Promise((resolve) => {
    setTimeout(() => {
      resolve()
    }, 3000)
  })
}

function stopPythonBackend() {
  if (pythonProcess) {
    console.log('Stopping Python backend...')
    
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', pythonProcess.pid, '/f', '/t'])
    } else {
      pythonProcess.kill('SIGTERM')
    }
    
    pythonProcess = null
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: true
    },
    icon: path.join(__dirname, '../public/favicon.ico'),
    show: false
  })

  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
  })

  if (isDev) {
    mainWindow.loadURL('http://localhost:5174/seoa/')
    mainWindow.webContents.openDevTools()
  } else {
    const indexPath = path.join(__dirname, '../dist/index.html')
    mainWindow.loadFile(indexPath)
  }

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })

  Menu.setApplicationMenu(null)
}

app.whenReady().then(async () => {
  try {
    await startPythonBackend()
    createWindow()
  } catch (error) {
    console.error('Failed to start application:', error)
    app.quit()
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  stopPythonBackend()
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', () => {
  stopPythonBackend()
})

app.on('will-quit', () => {
  stopPythonBackend()
})
