"use strict";
const require$$0 = require("electron");
var preload = {};
var hasRequiredPreload;
function requirePreload() {
  if (hasRequiredPreload) return preload;
  hasRequiredPreload = 1;
  const { contextBridge, ipcRenderer } = require$$0;
  contextBridge.exposeInMainWorld("electronAPI", {
    platform: process.platform,
    versions: {
      node: process.versions.node,
      chrome: process.versions.chrome,
      electron: process.versions.electron
    }
  });
  return preload;
}
requirePreload();
