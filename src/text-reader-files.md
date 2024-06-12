# Text reader files

Text reader files have the file extension `.zrd`, which could stand for Zipper Reader. Until 2022, I only knew of [binary reader files](reader-archives.md). However, there exist text reader files, for example `DefaultCtlConfig.zrd`.

## Investigation (MW3)

Although it was assumed the reader files were Lisp-like from the binary reader files, the text reader files confirm this:

```
(
  ⇥ KEYS (
  ⇥   ⇥ (CMD_ALPHASTRIKE  ⇥ keya(0x9c)  ⇥ joybtn(0x6))
  ⇥   ⇥ (CMD_AMS_TOGGLE  ⇥ keya(0x1e))
...
  ⇥ )
  ⇥ AXES (
  ⇥   ⇥ (Throttle  ⇥ joystick(Z)  ⇥ slope(-0.500000)  ⇥ intercept(0.500000)  ⇥ deadzone(0.050000))
  ⇥   ⇥ (Twist  ⇥ joystick(Rz)  ⇥ slope(-1.000000)  ⇥ intercept(0.000000)  ⇥ deadzone(0.000000))
  ⇥   ⇥ (Pitch  ⇥ joystick(Y)  ⇥ slope(1.000000)  ⇥ intercept(0.000000)  ⇥ deadzone(0.000000))
  ⇥   ⇥ (LR  ⇥ joystick(X)  ⇥ slope(-1.000000)  ⇥ intercept(0.000000)  ⇥ deadzone(0.000000))
  ⇥ )
)
```

Note that the whitespace delimiter used is a tab (indicated as ⇥ above).

There are a lot of interesting quirks with this lisp dialect. First, the whitespace delimiters are definitely tab, carriage return (CR), and line feed (LF), i.e. CR+LF don't seem to have a syntactic value. This is not unusual, but it isn't clear if a space is a valid delimiter. This also ties into the fact that strings don't seem to be quoted.

From the binary reader files, we know there are only four data types:

* Integers (i32)
* Floating-point numbers (f32, "floats")
* Strings
* Lists

Interestingly, the text reader files hint that at least mentally, there were more. For example, it seems like strings are always upper-case, and lower-case strings are symbols. This also leads to a concept of a "function" data type in the text reader, for example `joybtn(0x6)`. In other Lisps, this would've been written as `(joybtn 0x6)`. Also, maps/dictionaries are simply lists with implicit key-value pairs.

We don't know how the text reader files are precisely lexed. If I had to guess from binary reader files, the example above would be expressed in pseudo-JSON as follows:

```json
[
  "KEYS",
  [
    ["CMD_ALPHASTRIKE", "keya", [0x9c], "joybtn", [0x6]],
    ["CMD_AMS_TOGGLE", "keya", [0x1e]],
...
  ],
  "AXES",
  [
    ["Throttle", "joystick", ["Z"], "slope", [-0.5], "intercept", [0.5], "deadzone", [0.05]],
    ["Twist", "joystick", ["Rz"], "slope", [-1.0], "intercept", [0.0], "deadzone", [0.0]],
    ["Pitch", "joystick", ["Y"], "slope", [1.0], "intercept", [0.0], "deadzone", [0.0]],
    ["LR", "joystick", ["X"], "slope", [-1.0], "intercept", [0.0], "deadzone", [0.0]]
  ]
]
```

I believe the engine has an implicit schema, in that it tries to find string values by index, and then any information/arguments it needs are retrieved from index + 1.

There are still questions. For example, what happens if we mess with the order of "AXES"? Presumably when parsing, it looks at list index 0 to figure out what to put where in already existing data structures in the engine.

## Control configuration

The MechWarrior 3 engine uses DirectInput for controls. This also matches the key codes (`keya`) in the `DefaultCtlConfig.zrd`, they are DirectInput key codes. Below is a converter:

<p>
  <form action="">
    <div>
      <label for="keycode">Key code:</label>
      <input type="text" name="keycode" id="keycode" pattern="(0x[0-9a-fA-F]{1,3})|([0-9]{1,4})" placeholder="0x1" value="0x1" />
      <span id="keycode-valid"></span>
    </div>
    <hr />
    <div>
      <label for="mod-ctrl">Control:</label>
      <input type="checkbox" name="mod-ctrl" id="mod-ctrl" />
    </div>
    <div>
      <label for="mod-shift">Shift:</label>
      <input type="checkbox" name="mod-shift" id="mod-shift" />
    </div>
    <div>
      <label for="mod-alt">Alt:</label>
      <input type="checkbox" name="mod-alt" id="mod-alt" />
    </div>
    <div>
      <label for="keyname">Key name:</label>
      <input type="search" name="keyname" id="keyname" list="keyname-values" spellcheck="false" value="Esc" />
      <span id="keyname-valid"></span>
      <datalist id="keyname-values"></datalist>
    </div>
    <hr />
    <div>
      <label for="keycombo">Key combo:</label>
      <input type="text" name="keycombo" id="keycombo" readonly="true" />
    </div>
    <hr />
    <div>
      <label for="keyinput">Key input:</label>
      <input type="text" name="keyinput" id="keyinput" />
      <span id="keyinput-valid"></span>
      <br />
      <span>(try pressing some keys in the textbox)</span>
    </div>
    <input type="hidden" id="keybase" name="keybase" value="1" />
  </form>
</p>

<script>
const NAME_TO_CODE = new Map([
  ["Escape", 0x01],
  ["Esc", 0x01],
  ["1", 0x02],
  ["2", 0x03],
  ["3", 0x04],
  ["4", 0x05],
  ["5", 0x06],
  ["6", 0x07],
  ["7", 0x08],
  ["8", 0x09],
  ["9", 0x0A],
  ["0", 0x0B],
  ["Minus", 0x0C],
  ["-", 0x0C],
  ["Equals", 0x0D],
  ["=", 0x0D],
  ["Back", 0x0E],
  ["BackSpace", 0x0E],
  ["Tab", 0x0F],
  ["Q", 0x10],
  ["W", 0x11],
  ["E", 0x12],
  ["R", 0x13],
  ["T", 0x14],
  ["Y", 0x15],
  ["U", 0x16],
  ["I", 0x17],
  ["O", 0x18],
  ["P", 0x19],
  ["LBracket", 0x1A],
  ["[", 0x1A],
  ["RBracket", 0x1B],
  ["]", 0x1B],
  ["Return", 0x1C],
  ["Enter", 0x1C],
  ["LContol", 0x1D],
  ["Ctrl (Left)", 0x1D],
  ["A", 0x1E],
  ["S", 0x1F],
  ["D", 0x20],
  ["F", 0x21],
  ["G", 0x22],
  ["H", 0x23],
  ["J", 0x24],
  ["K", 0x25],
  ["L", 0x26],
  ["Semicolon", 0x27],
  [";", 0x27],
  ["Apostrophe", 0x28],
  ["'", 0x28],
  ["Grave", 0x29],
  ["`", 0x29],
  ["LShift", 0x2A],
  ["Shift (Left)", 0x2A],
  ["Backslash", 0x2B],
  ["\\", 0x2B],
  ["Z", 0x2C],
  ["X", 0x2D],
  ["C", 0x2E],
  ["V", 0x2F],
  ["B", 0x30],
  ["N", 0x31],
  ["M", 0x32],
  ["Comma", 0x33],
  [",", 0x33],
  ["Period", 0x34],
  [".", 0x34],
  ["Slash", 0x35],
  ["/", 0x35],
  ["RShift", 0x36],
  ["Shift (Right)", 0x36],
  ["Multiply (Numpad)", 0x37],
  ["* (Numpad)", 0x37],
  ["LMenu", 0x38],
  ["Alt (Left)", 0x38],
  ["Space", 0x39],
  ["CapsLock", 0x3A],
  ["F1", 0x3B],
  ["F2", 0x3C],
  ["F3", 0x3D],
  ["F4", 0x3E],
  ["F5", 0x3F],
  ["F6", 0x40],
  ["F7", 0x41],
  ["F8", 0x42],
  ["F9", 0x43],
  ["F10", 0x44],
  ["NumLock", 0x45],
  ["ScrollLock", 0x46],
  ["Numpad7", 0x47],
  ["7 (Numpad)", 0x47],
  ["Numpad8", 0x48],
  ["8 (Numpad)", 0x48],
  ["Numpad9", 0x49],
  ["9 (Numpad)", 0x49],
  ["Subtract (Numpad)", 0x4A],
  ["- (Numpad)", 0x4A],
  ["Numpad4", 0x4B],
  ["4 (Numpad)", 0x4B],
  ["Numpad5", 0x4C],
  ["5 (Numpad)", 0x4C],
  ["Numpad6", 0x4D],
  ["6 (Numpad)", 0x4D],
  ["Add (Numpad)", 0x4E],
  ["+ (Numpad)", 0x4E],
  ["Numpad1", 0x4F],
  ["1 (Numpad)", 0x4F],
  ["Numpad2", 0x50],
  ["2 (Numpad)", 0x50],
  ["Numpad3", 0x51],
  ["3 (Numpad)", 0x51],
  ["Numpad0", 0x52],
  ["0 (Numpad)", 0x52],
  ["Decimal (Numpad)", 0x53],
  ["Point (Numpad)", 0x53],
  [". (Numpad)", 0x53],
  ["F11", 0x57],
  ["F12", 0x58],
  ["Return (Numpad)", 0x9C],
  ["Enter (Numpad)", 0x9C],
  ["RControl", 0x9D],
  ["Ctrl (Right)", 0x9D],
  ["Divide (Numpad)", 0xB5],
  ["/ (Numpad)", 0xB5],
  ["Sys Rq", 0xB7],
  ["RMenu", 0xB8],
  ["Alt (Right)", 0xB8],
  ["Pause", 0xC5],
  ["Home", 0xC7],
  ["Up", 0xC8],
  ["PageUp", 0xC9],
  ["Left", 0xCB],
  ["Right", 0xCD],
  ["End", 0xCF],
  ["Down", 0xD0],
  ["PageDown", 0xD1],
  ["Insert", 0xD2],
  ["Delete", 0xD3],
  ["LWin", 0xDB],
  ["Windows (Left)", 0xDB],
  ["RWin", 0xDC],
  ["Windows (Right)", 0xDC],
]);

const CODE_TO_NAME = new Map([
  [0x01, "Esc"],
  [0x02, "1"],
  [0x03, "2"],
  [0x04, "3"],
  [0x05, "4"],
  [0x06, "5"],
  [0x07, "6"],
  [0x08, "7"],
  [0x09, "8"],
  [0x0A, "9"],
  [0x0B, "0"],
  [0x0C, "-"],
  [0x0D, "="],
  [0x0E, "BackSpace"],
  [0x0F, "Tab"],
  [0x10, "Q"],
  [0x11, "W"],
  [0x12, "E"],
  [0x13, "R"],
  [0x14, "T"],
  [0x15, "Y"],
  [0x16, "U"],
  [0x17, "I"],
  [0x18, "O"],
  [0x19, "P"],
  [0x1A, "["],
  [0x1B, "]"],
  [0x1C, "Enter"],
  [0x1D, "Ctrl (Left)"],
  [0x1E, "A"],
  [0x1F, "S"],
  [0x20, "D"],
  [0x21, "F"],
  [0x22, "G"],
  [0x23, "H"],
  [0x24, "J"],
  [0x25, "K"],
  [0x26, "L"],
  [0x27, ";"],
  [0x28, "'"],
  [0x29, "`"],
  [0x2A, "Shift (Left)"],
  [0x2B, "\\"],
  [0x2C, "Z"],
  [0x2D, "X"],
  [0x2E, "C"],
  [0x2F, "V"],
  [0x30, "B"],
  [0x31, "N"],
  [0x32, "M"],
  [0x33, ","],
  [0x34, "."],
  [0x35, "/"],
  [0x36, "Shift (Right)"],
  [0x37, "* (Numpad)"],
  [0x38, "Alt (Left)"],
  [0x39, "Space"],
  [0x3A, "CapsLock"],
  [0x3B, "F1"],
  [0x3C, "F2"],
  [0x3D, "F3"],
  [0x3E, "F4"],
  [0x3F, "F5"],
  [0x40, "F6"],
  [0x41, "F7"],
  [0x42, "F8"],
  [0x43, "F9"],
  [0x44, "F10"],
  [0x45, "NumLock"],
  [0x46, "ScrollLock"],
  [0x47, "7 (Numpad)"],
  [0x48, "8 (Numpad)"],
  [0x49, "9 (Numpad)"],
  [0x4A, "- (Numpad)"],
  [0x4B, "4 (Numpad)"],
  [0x4C, "5 (Numpad)"],
  [0x4D, "6 (Numpad)"],
  [0x4E, "+ (Numpad)"],
  [0x4F, "1 (Numpad)"],
  [0x50, "2 (Numpad)"],
  [0x51, "3 (Numpad)"],
  [0x52, "0 (Numpad)"],
  [0x53, ". (Numpad)"],
  [0x57, "F11"],
  [0x58, "F12"],
  [0x9C, "Enter (Numpad)"],
  [0x9D, "Ctrl (Right)"],
  [0xB5, "/ (Numpad)"],
  [0xB7, "Sys Rq"],
  [0xB8, "Alt (Right)"],
  [0xC5, "Pause"],
  [0xC7, "Home"],
  [0xC8, "Up"],
  [0xC9, "PageUp"],
  [0xCB, "Left"],
  [0xCD, "Right"],
  [0xCF, "End"],
  [0xD0, "Down"],
  [0xD1, "PageDown"],
  [0xD2, "Insert"],
  [0xD3, "Delete"],
  [0xDB, "Windows (Left)"],
  [0xDC, "Windows (Right)"],
]);

const BROWER_TO_CODE = new Map([
  ["Escape", 0x01],
  ["Digit1", 0x02],
  ["Digit2", 0x03],
  ["Digit3", 0x04],
  ["Digit4", 0x05],
  ["Digit5", 0x06],
  ["Digit6", 0x07],
  ["Digit7", 0x08],
  ["Digit8", 0x09],
  ["Digit9", 0x0A],
  ["Digit0", 0x0B],
  ["Minus", 0x0C],
  ["Equal", 0x0D],
  ["Backspace", 0x0E],
  ["Tab", 0x0F],
  ["KeyQ", 0x10],
  ["KeyW", 0x11],
  ["KeyE", 0x12],
  ["KeyR", 0x13],
  ["KeyT", 0x14],
  ["KeyY", 0x15],
  ["KeyU", 0x16],
  ["KeyI", 0x17],
  ["KeyO", 0x18],
  ["KeyP", 0x19],
  ["BracketLeft", 0x1A],
  ["BracketRight", 0x1B],
  ["Enter", 0x1C],
  ["ControlLeft", 0x1D],
  ["KeyA", 0x1E],
  ["KeyS", 0x1F],
  ["KeyD", 0x20],
  ["KeyF", 0x21],
  ["KeyG", 0x22],
  ["KeyH", 0x23],
  ["KeyJ", 0x24],
  ["KeyK", 0x25],
  ["KeyL", 0x26],
  ["Semicolon", 0x27],
  ["Quote", 0x28],
  ["Backquote", 0x29],
  ["ShiftLeft", 0x2A],
  ["Backslash", 0x2B],
  ["KeyZ", 0x2C],
  ["KeyX", 0x2D],
  ["KeyC", 0x2E],
  ["KeyV", 0x2F],
  ["KeyB", 0x30],
  ["KeyN", 0x31],
  ["KeyM", 0x32],
  ["Comma", 0x33],
  ["Period", 0x34],
  ["Slash", 0x35],
  ["ShiftRight", 0x36],
  ["NumpadMultiply", 0x37],
  ["AltLeft", 0x38],
  ["Space", 0x39],
  ["CapsLock", 0x3A],
  ["F1", 0x3B],
  ["F2", 0x3C],
  ["F3", 0x3D],
  ["F4", 0x3E],
  ["F5", 0x3F],
  ["F6", 0x40],
  ["F7", 0x41],
  ["F8", 0x42],
  ["F9", 0x43],
  ["F10", 0x44],
  ["NumLock", 0x45],
  ["ScrollLock", 0x46],
  ["Numpad7", 0x47],
  ["Numpad8", 0x48],
  ["Numpad9", 0x49],
  ["NumpadSubtract", 0x4A],
  ["Numpad4", 0x4B],
  ["Numpad5", 0x4C],
  ["Numpad6", 0x4D],
  ["NumpadAdd", 0x4E],
  ["Numpad1", 0x4F],
  ["Numpad2", 0x50],
  ["Numpad3", 0x51],
  ["Numpad0", 0x52],
  ["NumpadDecimal", 0x53],
  ["F11", 0x57],
  ["F12", 0x58],
  ["NumpadEnter", 0x9C],
  ["ControlRight", 0x9D],
  ["NumpadDivide", 0xB5],
  ["AltRight", 0xB8],
  ["Pause", 0xC5],
  ["Home", 0xC7],
  ["ArrowUp", 0xC8],
  ["PageUp", 0xC9],
  ["ArrowLeft", 0xCB],
  ["ArrowRight", 0xCD],
  ["End", 0xCF],
  ["ArrowDown", 0xD0],
  ["PageDown", 0xD1],
  ["Insert", 0xD2],
  ["Delete", 0xD3],
  // Firefox
  ["OSLeft", 0xDB],
  ["OSRight", 0xDC],
  // Chome
  ["MetaLeft", 0xDB],
  ["MetaRight", 0xDC],
]);

const ALT_MASK = 0x100;
const CTRL_MASK = 0x200;
const SHIFT_MASK = 0x400;
const MOD_MASK = ALT_MASK | CTRL_MASK | SHIFT_MASK;

function populateKeynameDatalist() {
  const datalist_el = document.querySelector("#keyname-values");
  for (const name of NAME_TO_CODE.keys()) {
    const option_el = document.createElement("option");
    option_el.value = name;
    datalist_el.appendChild(option_el);
  }
}

document.addEventListener("DOMContentLoaded", _ => {
  populateKeynameDatalist();

  const keybase_el = document.querySelector("#keybase");
  const keycode_el = document.querySelector("#keycode");
  const keyname_el = document.querySelector("#keyname");
  const keycombo_el = document.querySelector("#keycombo");
  const keyinput_el = document.querySelector("#keyinput");

  const mod_ctrl_el = document.querySelector("#mod-ctrl");
  const mod_shift_el = document.querySelector("#mod-shift");
  const mod_alt_el = document.querySelector("#mod-alt");

  const keycode_valid_el = document.querySelector("#keycode-valid");
  const keyname_valid_el = document.querySelector("#keyname-valid");
  const keyinput_valid_el = document.querySelector("#keyinput-valid");

  keycode_el.addEventListener("input", e => {
    const keycode_raw = e.target.value;
    // skip empty input by doing nothing (not even an error)
    if (keycode_raw.length == 0) {
      keycode_valid_el.textContent = "";
      return;
    }
    keyname_el.value = "";
    keyname_valid_el.textContent = "";
    keyinput_valid_el.textContent = "";
    // parse the keycode to either hex or dec
    let code = NaN;
    if (keycode_raw.startsWith("0x")) {
      code = parseInt(keycode_raw.substr(2), 16);
    } else {
      code = parseInt(keycode_raw.substr(0), 10);
    }
    if (isNaN(code)) {
      keycode_valid_el.textContent = "❌ (could not convert)";
      return;
    }
    // sort out modifiers
    const has_ctrl = (code & CTRL_MASK) == CTRL_MASK;
    const has_shift = (code & SHIFT_MASK) == SHIFT_MASK;
    const has_alt = (code & ALT_MASK) == ALT_MASK;
    const base = (code & (~MOD_MASK));
    if (base > 0xFF) {
      keycode_valid_el.textContent = "❌ (unknown modifier?)";
      return;
    }
    // look up the key name
    const name = CODE_TO_NAME.get(base);
    if (name === undefined) {
      keycode_valid_el.textContent = "❌ (unknown key)";
      return;
    }
    // done
    const combo = [];
    mod_ctrl_el.checked = has_ctrl;
    if (has_ctrl) {
      combo.push("Ctrl");
    }
    mod_shift_el.checked = has_shift;
    if (has_ctrl) {
      combo.push("Shift");
    }
    mod_alt_el.checked = has_alt;
    if (has_ctrl) {
      combo.push("Alt");
    }
    combo.push(name);
    keybase_el.value = base;
    keycode_valid_el.textContent = "✅";
    keyname_el.value = name;
    keyname_valid_el.textContent = "✅";
    keycombo_el.value = combo.join("+");
  });

  keyname_el.addEventListener("input", e => {
    const keyname_raw = e.target.value;
    // skip empty input by doing nothing (not even an error)
    if (keyname_raw.length == 0) {
      keyname_valid_el.textContent = "";
      return;
    }
    keycode_el.value = "";
    keycode_valid_el.textContent = "";
    keyinput_valid_el.textContent = "";
    // look up the key name
    const base = NAME_TO_CODE.get(keyname_raw);
    if (base === undefined) {
      keyname_valid_el.textContent = "❌ (unknown key)";
      return;
    }
    const name = CODE_TO_NAME.get(base);
    const combo = [];
    // sort out modifiers
    let code = base;
    if (mod_ctrl_el.checked) {
      code |= CTRL_MASK;
      combo.push("Ctrl");
    }
    if (mod_shift_el.checked) {
      code |= SHIFT_MASK;
      combo.push("Shift");
    }
    if (mod_alt_el.checked) {
      code |= ALT_MASK;
      combo.push("Alt");
    }
    combo.push(name);
    // done
    keybase_el.value = base;
    keycode_el.value = "0x" + code.toString(16);
    keycode_valid_el.textContent = "✅";
    keycombo_el.value = combo.join("+");
    keyname_valid_el.textContent = "✅";
  });

  function updateCodeFromModifier(e) {
    keyinput_valid_el.textContent = "";
    // look up the key base
    const base = Number(keybase_el.value);
    const name = CODE_TO_NAME.get(base);
    // sort out modifiers
    let code = base;
    const combo = [];
    if (mod_ctrl_el.checked) {
      code |= CTRL_MASK;
      combo.push("Ctrl");
    }
    if (mod_shift_el.checked) {
      code |= SHIFT_MASK;
      combo.push("Shift");
    }
    if (mod_alt_el.checked) {
      code |= ALT_MASK;
      combo.push("Alt");
    }
    combo.push(name);
    // done
    keycode_el.value = "0x" + code.toString(16);
    keycode_valid_el.textContent = "✅";
    keycombo_el.value = combo.join("+");
  }

  mod_ctrl_el.addEventListener("input", updateCodeFromModifier);
  mod_shift_el.addEventListener("input", updateCodeFromModifier);
  mod_alt_el.addEventListener("input", updateCodeFromModifier);

  keyinput_el.addEventListener("keydown", e => {
    if (event.isComposing || event.keyCode === 229) {
      return;
    }
    e.preventDefault();

    if (e.metaKey) {
      keyinput_valid_el.textContent = "❌ (unknown Windows key, Command/Meta held)";
      return;
    }

    const base = BROWER_TO_CODE.get(event.code);
    if (base === undefined) {
      keyinput_valid_el.textContent = "❌ (unknown key)";
      return;
    }

    const name = CODE_TO_NAME.get(base);
    const combo = [];
    const has_ctrl = e.ctrlKey;
    const has_shift = e.shiftKey;
    const has_alt = e.altKey;
    // sort out modifiers
    let code = base;
    if (has_ctrl) {
      code |= CTRL_MASK;
      combo.push("Ctrl");
    }
    if (has_shift) {
      code |= SHIFT_MASK;
      combo.push("Shift");
    }
    // Alt or Option (macOS)
    if (has_alt) {
      code |= ALT_MASK;
      combo.push("Alt");
    }
    combo.push(name);
    // done
    mod_ctrl_el.checked = has_ctrl;
    mod_shift_el.checked = has_shift;
    mod_alt_el.checked = has_alt;
    keycode_el.value = "0x" + code.toString(16);
    keycode_valid_el.textContent = "✅";
    keyname_el.value = name;
    keyname_valid_el.textContent = "✅";
    keycombo_el.value = combo.join("+");
    keyinput_valid_el.textContent = "✅";
  });
});

</script>
