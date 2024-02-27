# Ditto
___
This is inspired by how Jetbrains updates the Unreal Link IDE plugin

---

## Program Features:

- Copy folders from a plugin in a launcher-based engine folder to source build(s)
- Pick which plugins to copy
- Locate Engine installations?
  - or at the very least add them manually
- Compile the plugin if needed?
- Check if the launcher plugin(s) was updated?

---
## Unreal Folder Plugin Folder Structure:

| Folder         |
|----------------|
| (Binaries)     |
| (Config)       |
| Content        |
| (Intermediate) |
| (Resources)    |
| Source         |
| (Shaders)      |
| (ThirdParty)   |

Folders in parentheses are either:
- generated when the plugin is compiled
- as required when needed.
