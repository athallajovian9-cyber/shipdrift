#!/usr/bin/env node
"use strict";

// Sync the Python package into the npm package before packing.

const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..", "..");
const pkg = "shipdrift";
const src = path.join(root, pkg);
const dst = path.join(__dirname, "..", "lib", pkg);

fs.rmSync(path.join(__dirname, "..", "lib"), { recursive: true, force: true });
fs.mkdirSync(dst, { recursive: true });

for (const f of fs.readdirSync(src)) {
  if (f.endsWith(".py")) fs.copyFileSync(path.join(src, f), path.join(dst, f));
}
fs.copyFileSync(path.join(root, "LICENSE"), path.join(__dirname, "..", "LICENSE"));
fs.copyFileSync(path.join(root, "README.md"), path.join(__dirname, "..", "README.md"));

console.log("synced " + fs.readdirSync(dst).length + " modules into npm/lib/" + pkg);
