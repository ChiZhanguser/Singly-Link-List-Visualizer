from . import linkedlist_dsl
from . import stack_dsl
from . import sequence_dsl
from . import bst_dsl
from . import trie_dsl
from . import huffman_dsl
from . import avl_dsl  
from . import rbt_dsl

def process_command(visualizer, text):
    if not visualizer or not text or not text.strip():
        return

    print(f"DEBUG: Processing command for visualizer: {type(visualizer).__name__}")
    print(f"DEBUG: Command text: {text}")
    visualizer_type = type(visualizer).__name__.lower()

    try:
        # Huffman visualizer
        if ("huffman" in visualizer_type or
            hasattr(visualizer, "start_animated_build") and hasattr(visualizer, "clear_canvas")):
            print(f"DEBUG: Processing as Huffman visualizer")
            return huffman_dsl.process(visualizer, text)
    except Exception as e:
        print(f"DEBUG: Huffman processing error: {e}")
        pass
    
    try:
        # LinkList or LinkedListVisualizer
        if type(visualizer).__name__ in ("LinkList", "LinkedListVisualizer") or "linked" in visualizer_type:
            print(f"DEBUG: Processing as LinkedList visualizer")
            return linkedlist_dsl.process(visualizer, text)
            
        if (hasattr(visualizer, "node_value_store") or 
            "linked" in visualizer_type or 
            "link" in visualizer_type or
            "linklist" in visualizer_type):
            print(f"DEBUG: Matched linked list by other criteria")
            return linkedlist_dsl.process(visualizer, text)
    except Exception as e:
        print(f"Error in linked list command processing: {e}")  
        pass
    
    try:
        # Circular Queue Visualizer (检查要放在栈之前,因为条件更具体)
        if ("circularqueue" in visualizer_type.replace("_", "") or
            "queue" in visualizer_type.lower() or
            hasattr(visualizer, "animate_enqueue") and hasattr(visualizer, "animate_dequeue")):
            print(f"DEBUG: Processing as Circular Queue visualizer")
            text_parts = text.strip().split()
            if not text_parts:
                return
            
            cmd = text_parts[0].lower()
            args = text_parts[1:]
            
            # Command conversion for queue operations
            if cmd in ("insert", "add", "push"):
                text = "enqueue " + " ".join(args)
            elif cmd in ("delete", "remove", "pop"):
                text = "dequeue"
            print(f"DEBUG: Circular Queue command conversion: {text}")
            from . import circular_queue_dsl
            return circular_queue_dsl._fallback_process_command(visualizer, text)
    except Exception as e:
        print(f"DEBUG: Circular Queue processing error: {e}")
        pass

    try:
        if ("stack" in visualizer_type or 
            hasattr(visualizer, "animate_push_left") or
            (hasattr(visualizer, "model") and 
             hasattr(visualizer.model, "is_full") and 
             not hasattr(visualizer, "animate_enqueue"))):  # 确保不是队列
            print(f"DEBUG: Processing as Stack visualizer")
            text_parts = text.strip().split()
            if not text_parts:
                return
            
            cmd = text_parts[0].lower()
            args = text_parts[1:]
            
            if cmd in ("insert", "add"):
                text = "push " + " ".join(args)
            elif cmd == "delete":
                if len(args) > 0 and args[0].lower() in ("last", "tail"):
                    text = "pop"
                else:
                    pass
            print(f"DEBUG: Stack command conversion: {text}")
            return stack_dsl.process(visualizer, text)
    except Exception as e:
        print(f"DEBUG: Stack processing error: {e}")
        pass

    try:
        # Sequence List Visualizer
        if ("sequence" in visualizer_type or
            hasattr(visualizer, "animate_build_element") or
            hasattr(visualizer, "animate_insert")):
            print(f"DEBUG: Processing as Sequence List visualizer")
            return sequence_dsl.process(visualizer, text)
    except Exception as e:
        print(f"DEBUG: Sequence processing error: {e}")
        pass

    try:
        # Red-Black Tree Visualizer (在AVL之前检查,避免混淆)
        if ("rbt" in visualizer_type or 
            "redblack" in visualizer_type.replace("_", "").replace("-", "") or
            (hasattr(visualizer, "model") and 
             hasattr(visualizer.model, "root") and
             hasattr(visualizer, "start_insert_animated") and
             # 检查节点是否有color属性(红黑树特征)
             (visualizer.model.root is None and hasattr(visualizer.model.root, "color")))):
            print(f"DEBUG: Processing as Red-Black Tree visualizer")
            return rbt_dsl.process(visualizer, text)
    except Exception as e:
        print(f"DEBUG: RBT processing error: {e}")
        pass

    try:
        # AVL Visualizer
        if ("avl" in visualizer_type or 
            hasattr(visualizer, "start_insert_animated") and 
            hasattr(visualizer, "clear_canvas") and
            hasattr(visualizer, "model") and
            hasattr(visualizer.model, "_balance_factor")):
            print(f"DEBUG: Processing as AVL visualizer")
            return avl_dsl.process(visualizer, text)
    except Exception as e:
        print(f"DEBUG: AVL processing error: {e}")
        pass
    
    try:
        # Binary Search Tree Visualizer
        if ("bst" in visualizer_type or
            hasattr(visualizer, "start_insert_animated") and
            hasattr(visualizer, "start_search_animated")):
            print(f"DEBUG: Processing as BST visualizer")
            return bst_dsl.process(visualizer, text)
    except Exception as e:
        print(f"DEBUG: BST processing error: {e}")
        pass

    try:
        # Trie Visualizer
        if ("trie" in visualizer_type or
            hasattr(visualizer, "clear_trie") or
            hasattr(visualizer, "start_insert_animated") and not "bst" in visualizer_type):
            print(f"DEBUG: Processing as Trie visualizer")
            return trie_dsl.process(visualizer, text)
    except Exception as e:
        print(f"DEBUG: Trie processing error: {e}")
        pass
    
    from tkinter import messagebox
    messagebox.showinfo("未识别可视化类型", 
        "当前支持的数据结构类型：\n"
        "1. 单链表 (LinkedList)\n"
        "2. 栈 (Stack)\n"
        "3. 顺序表 (Sequence List)\n"
        "4. 二叉搜索树 (BST)\n"
        "5. AVL树 (AVL)\n"
        "6. 红黑树 (RBT)\n"
        "7. 字典树 (Trie)\n"
        "8. 哈夫曼树 (Huffman)\n\n"
        f"当前类型 '{type(visualizer).__name__}' 未能匹配到对应的DSL处理器。")