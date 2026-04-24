import require$$0 from "electron";
import require$$1 from "path";
import require$$2 from "child_process";
import require$$3 from "fs";
function getDefaultExportFromCjs(x) {
  return x && x.__esModule && Object.prototype.hasOwnProperty.call(x, "default") ? x["default"] : x;
}
var main$1 = {};
var hasRequiredMain;
function requireMain() {
  if (hasRequiredMain) return main$1;
  hasRequiredMain = 1;
  const { app, BrowserWindow, Menu, shell } = require$$0;
  const path = require$$1;
  const { spawn } = require$$2;
  const fs = require$$3;
  let mainWindow = null;
  let pythonProcess = null;
  const isDev = !app.isPackaged;
  function getPythonPath() {
    if (isDev) {
      return "python";
    }
    const resourcePath = process.resourcesPath;
    const pythonPath = path.join(resourcePath, "python", "python.exe");
    if (fs.existsSync(pythonPath)) {
      return pythonPath;
    }
    return "python";
  }
  function getBackendPath() {
    if (isDev) {
      return path.join(__dirname, "..", "..", "Back_end", "main.py");
    }
    return path.join(process.resourcesPath, "Back_end", "main.py");
  }
  function startPythonBackend() {
    const pythonPath = getPythonPath();
    const backendPath = getBackendPath();
    console.log("Starting Python backend...");
    console.log("Python path:", pythonPath);
    console.log("Backend path:", backendPath);
    const backendDir = path.dirname(backendPath);
    pythonProcess = spawn(pythonPath, [backendPath], {
      cwd: backendDir,
      env: { ...process.env },
      stdio: ["ignore", "pipe", "pipe"]
    });
    pythonProcess.stdout.on("data", (data) => {
      console.log(`Backend stdout: ${data}`);
    });
    pythonProcess.stderr.on("data", (data) => {
      console.error(`Backend stderr: ${data}`);
    });
    pythonProcess.on("error", (err) => {
      console.error("Failed to start Python backend:", err);
    });
    pythonProcess.on("close", (code) => {
      console.log(`Python backend exited with code ${code}`);
      pythonProcess = null;
    });
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve();
      }, 3e3);
    });
  }
  function stopPythonBackend() {
    if (pythonProcess) {
      console.log("Stopping Python backend...");
      if (process.platform === "win32") {
        spawn("taskkill", ["/pid", pythonProcess.pid, "/f", "/t"]);
      } else {
        pythonProcess.kill("SIGTERM");
      }
      pythonProcess = null;
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
        preload: path.join(__dirname, "preload.cjs"),
        webSecurity: true
      },
      icon: path.join(__dirname, "../public/favicon.ico"),
      show: false
    });
    mainWindow.once("ready-to-show", () => {
      mainWindow.show();
    });
    if (isDev) {
      mainWindow.loadURL("http://localhost:5174/seoa/");
      mainWindow.webContents.openDevTools();
    } else {
      const indexPath = path.join(__dirname, "../dist/index.html");
      mainWindow.loadFile(indexPath);
    }
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
      shell.openExternal(url);
      return { action: "deny" };
    });
    mainWindow.on("closed", () => {
      mainWindow = null;
    });
    const menuTemplate = [
      {
        label: "文件",
        submenu: [
          { role: "quit", label: "退出" }
        ]
      },
      {
        label: "视图",
        submenu: [
          { role: "reload", label: "刷新" },
          { role: "toggleDevTools", label: "开发者工具" },
          { type: "separator" },
          { role: "resetZoom", label: "重置缩放" },
          { role: "zoomIn", label: "放大" },
          { role: "zoomOut", label: "缩小" },
          { type: "separator" },
          { role: "togglefullscreen", label: "全屏" }
        ]
      },
      {
        label: "帮助",
        submenu: [
          {
            label: "关于",
            click: () => {
              const { dialog } = require$$0;
              dialog.showMessageBox(mainWindow, {
                type: "info",
                title: "关于 SEOA",
                message: "化学实验评价系统",
                detail: "版本: 1.0.0\n一个基于现代Web技术开发的实验教学辅助平台"
              });
            }
          }
        ]
      }
    ];
    const menu = Menu.buildFromTemplate(menuTemplate);
    Menu.setApplicationMenu(menu);
  }
  app.whenReady().then(async () => {
    try {
      await startPythonBackend();
      createWindow();
    } catch (error) {
      console.error("Failed to start application:", error);
      app.quit();
    }
    app.on("activate", () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
      }
    });
  });
  app.on("window-all-closed", () => {
    stopPythonBackend();
    if (process.platform !== "darwin") {
      app.quit();
    }
  });
  app.on("before-quit", () => {
    stopPythonBackend();
  });
  app.on("will-quit", () => {
    stopPythonBackend();
  });
  return main$1;
}
var mainExports = requireMain();
const main = /* @__PURE__ */ getDefaultExportFromCjs(mainExports);
export {
  main as default
};
