# dsl_interpreter.py
# 纯 Python 的最小 DSL 解析器 + 解释器 -> 生成 AST/JSON -> 调用模型 API
import re
import json
from typing import List, Dict, Any, Tuple, Optional

# ---- 解析器（非常简单的行级解析） ----
TOKEN_RE = re.compile(r'''
    (?P<STR>"[^"]*"|'[^']*') |
    (?P<NAME>[A-Za-z_][A-Za-z0-9_]*) |
    (?P<NUM>-?\d+(\.\d+)?) |
    (?P<LBR>\[) |
    (?P<RBR>\]) |
    (?P<COM>,) |
    (?P<HASH>\#) |
    (?P<WS>\s+) |
    (?P<OTHER>.)
''', re.X)

def tokenize_line(line:str):
    tokens=[]
    for m in TOKEN_RE.finditer(line):
        if m.lastgroup == 'WS': continue
        tokens.append((m.lastgroup, m.group(0)))
    return tokens

def parse_values_tokenlist(tokens:List[Tuple[str,str]], start_idx=0)->Tuple[List[str], int]:
    """
    解析 1,2,3 或 [1,2,#,4]
    返回 (list_of_values_as_strings, next_index)
    """
    vals=[]
    i=start_idx
    # allow optional leading '['
    if i < len(tokens) and tokens[i][0] == 'LBR':
        i += 1
        expect_val = True
        while i < len(tokens):
            typ, tok = tokens[i]
            if typ in ('STR','NAME','NUM','HASH'):
                vals.append(tok.strip('"').strip("'"))
                i += 1
                expect_val=False
            elif typ == 'COM':
                i += 1
                expect_val = True
            elif typ == 'RBR':
                i += 1
                break
            else:
                # skip unknown
                i += 1
        return vals, i
    else:
        # parse simple comma-sep list until end
        while i < len(tokens):
            typ, tok = tokens[i]
            if typ in ('NUM','NAME','STR','HASH'):
                vals.append(tok.strip('"').strip("'"))
                i += 1
            elif typ == 'COM':
                i += 1
            else:
                break
        return vals, i

def parse_dsl(text:str)->List[Dict[str,Any]]:
    """
    把 DSL 文本解析为命令字典列表（AST）
    支持注释 # 开头
    """
    lines = text.splitlines()
    cmds=[]
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith('#'): continue
        tokens = tokenize_line(line)
        # simplify: first word is command
        if not tokens: continue
        first_type, first_tok = tokens[0]
        cmd_name = first_tok.lower()
        # handle various commands
        if cmd_name in ('create',):
            # create <kind> <name>
            if len(tokens) >= 3:
                kind = tokens[1][1].lower()
                name = tokens[2][1]
                cmds.append({"op":"create","kind":kind,"name":name})
        elif cmd_name in ('insert',):
            # insert <name> 1,2,3
            if len(tokens) >= 2:
                name = tokens[1][1]
                vals, _ = parse_values_tokenlist(tokens, 2)
                cmds.append({"op":"insert","name":name,"values":vals})
        elif cmd_name in ('build_tree',):
            # build_tree X [1,2,3,#,4]
            if len(tokens) >= 2:
                name = tokens[1][1]
                vals, _ = parse_values_tokenlist(tokens, 2)
                cmds.append({"op":"build_tree","name":name,"values":vals})
        elif cmd_name in ('visualize',):
            # visualize name [optional args]
            name = tokens[1][1] if len(tokens)>=2 else None
            args = [t[1] for t in tokens[2:]]
            cmds.append({"op":"visualize","name":name,"args":args})
        elif cmd_name in ('save',):
            # save name "path"
            if len(tokens)>=3:
                name = tokens[1][1]
                path = tokens[2][1].strip('"').strip("'")
                cmds.append({"op":"save","name":name,"path":path})
        elif cmd_name in ('load',):
            # load "path" as NAME
            # find STR token or NAME token
            # naive: second token is path, possibly quoted
            if len(tokens) >= 2:
                path_tok = tokens[1][1].strip('"').strip("'")
                # optional 'as' <name>
                as_name = None
                if len(tokens) >= 4 and tokens[2][1].lower() == 'as':
                    as_name = tokens[3][1]
                cmds.append({"op":"load","path":path_tok,"as":as_name})
        elif cmd_name in ('step',):
            # step insert T 9  -> step <action> <name> <args...>
            if len(tokens)>=2:
                action = tokens[1][1].lower()
                if action == 'insert' and len(tokens)>=4:
                    name = tokens[2][1]
                    vals, _ = parse_values_tokenlist(tokens, 3)
                    cmds.append({"op":"step_insert","name":name,"values":vals})
                else:
                    # generic step
                    cmds.append({"op":"step_generic","tokens":[t[1] for t in tokens[1:]]})
        else:
            # unknown: put raw
            cmds.append({"op":"raw","line":line})
    return cmds

# ---- 解释器：把 AST -> 调用到模型/visualizer（需要你项目里的模型类） ----
# 下面是一个调用示例，里面注释了你需要把它与项目模型对接的地方。
def interpret(cmds:List[Dict[str,Any]], env:Dict[str,Any]):
    """
    env: 一个 dict，用于注入项目模型类与可视化控制接口，例如:
      env = {
         "models": {},   # 名称 -> model instance
         "classes": { "bst": BSTModel, "avl": AVLModel, "huffman": HuffmanModel, ... },
         "visualizers": { "bst": BinaryTreeVisualizerClass, ... },
         "save_func": storage.save_tree_to_file, "load_func": storage.load_tree_from_file
      }
    """
    models = env.setdefault("models", {})
    classes = env.get("classes", {})
    vis_map = env.get("visualizers", {})
    save_func = env.get("save_func")
    load_func = env.get("load_func")
    results = []
    for c in cmds:
        op = c.get("op")
        if op == "create":
            kind = c["kind"]
            name = c["name"]
            cls = classes.get(kind)
            if not cls:
                print(f"[WARN] unknown kind {kind} — skip create")
                continue
            inst = cls()  # 例如 BSTModel()
            models[name] = inst
            print(f"Created {kind} {name}")
            results.append(("created",name))
        elif op == "insert":
            name = c["name"]
            vals = c["values"]
            m = models.get(name)
            if not m:
                print(f"[WARN] model {name} not found")
                continue
            # NOTE: here we try a few common API patterns
            # 1) if m has insert_with_steps, call it per value
            if hasattr(m, "insert_with_steps"):
                for v in vals:
                    m.insert_with_steps(v)
            elif hasattr(m, "insert"):
                for v in vals:
                    m.insert(v)
            elif hasattr(m, "push"):
                for v in vals:
                    m.push(v)
            elif hasattr(m, "build_with_steps") and isinstance(vals, list):
                # for Huffman-like: treat as build sequence
                m.build_with_steps([float(x) for x in vals])
            else:
                # fallback: if it's a model exposing .data list
                if hasattr(m, "data"):
                    m.data.extend(vals)
            results.append(("inserted", name, vals))
        elif op == "build_tree":
            name = c["name"]; vals = c["values"]
            m = models.get(name)
            if not m:
                print(f"[WARN] model {name} not found for build_tree")
                continue
            # if it's a binary-tree-like model and it has from_level_order or similar, try to use it
            if hasattr(m, "from_level_order"):
                m.from_level_order(vals)
            else:
                # naive: build by inserting values in level order (with # as None)
                # If your BinaryTreeVisualizer expects a root node, you may need to call storage.tree_dict_to_nodes
                if hasattr(m, "insert"):
                    for v in vals:
                        if v == "#": continue
                        m.insert(v)
            results.append(("built", name))
        elif op == "visualize":
            name = c.get("name")
            if not name:
                # global visualize?
                continue
            m = models.get(name)
            if not m:
                print(f"[WARN] model {name} not found for visualize")
                continue
            # If you have a visualizer mapped, call it
            vis_cls = vis_map.get(name) or vis_map.get(type(m).__name__.lower())
            if vis_cls:
                # instantiate and pass model to visualizer — depends on your visualizer design
                # example: vis = vis_cls(model=m); vis.show()
                vis_obj = vis_cls(m)  # adapt to your constructor
            results.append(("visualized", name))
        elif op == "save":
            name = c["name"]; path = c["path"]
            m = models.get(name)
            if not m:
                print(f"[WARN] model {name} not found for save")
                continue
            if save_func:
                save_func(getattr(m, "root", None), filepath=path)
                print("Saved", path)
            results.append(("saved", name, path))
        elif op == "load":
            path = c["path"]; as_name=c.get("as")
            if load_func:
                d = load_func(filepath=path)
                # d is a tree dict; user needs to convert
                results.append(("loaded", path, as_name))
        else:
            print("Unknown op:", c)
    return results

# ---- convenience runner ----
def run_dsl_text(text:str, env:Dict[str,Any]):
    ast = parse_dsl(text)
    print("AST:", json.dumps(ast, indent=2, ensure_ascii=False))
    res = interpret(ast, env)
    return res

if __name__ == "__main__":
    sample = """
    # demo
    create avl A
    insert A 1,2,3
    visualize A
    save A "out/avl1.json"
    """
    # env must inject model classes from your project.
    env = {"classes": { "avl": lambda: print("dummy") } }
    print(run_dsl_text(sample, env))
