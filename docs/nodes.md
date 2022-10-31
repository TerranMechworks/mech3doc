# Nodes

Nodes are how the world data is organised and structured. Nodes appear in GameZ files and mechlib archives. There are eight known node types in GameZ files:

* Camera
* Display
* Empty
* Light
* LOD (level of detail)
* Object3d
* Window
* World

In MechWarrior 3, the only valid node type in the mechlib archive is Object3d. In Pirate's Moon, the only valid node types in the mechlib archive are Object3d and LOD.

We also think there are other node types from the animations:

* Sequence
* Animate or Animation
* Sound
* Switch (i.e. flow control)

Each node type has the same base structure, although some node types do not seem to use all the information in the base structure. The node types also have node-specific structures/information.

## Node organisation/relationships

Each node can have several parents, and several children. In fact, each node tracks both the children and the parents, and there doesn't seem to be a way of ensuring this data is consistent other than careful coding (e.g. when a child is removed, also remove it's reference to the parent).

In principle, this results in a directed graph structure. Cycles are also absolutely possible. Again this was presumably carefully avoided because a cyclic graph is not useful for most processing. Let's assume therefore that a valid representation of nodes inside the engine is a directed acyclic graph (DAG) at the very least.

In reality, the nodes are usually tree-like, although in a "tree" in the computer science sense, there can only be one root, and each node has exactly one parent. From what I can see, this isn't necessarily the case for MW3. Otherwise, why allow a node to have multiple parents?

However, when loading nodes from the mechlib or GameZ files, the nodes indeed only have either zero (0) or one (1) parent (at load time). We'll discuss further restrictions on the different node types shortly.

## Common data types

```rust
tuple Vec3(f32, f32, f32);
tuple Color(f32, f32, f32);
tuple Matrix(f32, f32, f32, f32, f32, f32, f32, f32, f32);

const MATRIX_EMPTY: Matrix = Matrix(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
const MATRIX_IDENTITY: Matrix = Matrix(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0);
```

## Node data structures

* Node data structures [in the base game (MW3)](nodes-mw.md)
* Node data structures [in the expansion (PM)](nodes-pm.md) (incomplete)

## Node parents and children

In principle, all nodes could have multiple parents, and multiple children. In practice, no nodes have multiple parents, and as described in the node organisation and in the game-specific node data structures:

* Camera nodes don't have a parent or children
* Display nodes don't have a parent or children
* Empty nodes don't have a parent or children (at least not for the purposes of this part)
* Light nodes don't have a parent or children
* LOD nodes always have a parent, and always have children
* Object3d nodes can have a parent and children
* Window nodes don't have a parent or children
* World nodes don't have a parent, but do have children

The reason I describe this in such detail is that it helps understand how the game nodes are structured.

In the general case, both the parent and children indices are dynamic arrays. Read parent count u32 values first for the parent index/indices, and then read child count u32 values next for the child indices. (Obviously, if the count is zero, it isn't necessary to read anything.)

## Node positions in the GameZ file

There are also restrictions on which nodes can appear where in a GameZ file. Mechlib archives can only contain certain nodes, so this does not apply.

When loading a GameZ file:

* There can only be a single world node, and it must be the first node in the file (index 0)
* There can only be a single window node, and it must be the second node in the file (index 1)
* There can only be a single camera node, and it must be the third node in the file (index 2)
* There is at least one display node, and it must be the fourth node in the file (index 3). If there is another display node, it must be the fifth node in the file (index 4)
* There can only be a single light node, although its position in the file is variable
* Zeroed out nodes must be at the end of the array, and contiguous.
