# demo.dsl - 示例 DSL 脚本（保存为 DS_visual/demo.dsl）
# 创建几个结构并做简单操作与保存
create avl A
insert A 1,2,3
visualize A

create huffman H
insert H 1,2,3,4
visualize H

# 构造一个链式二叉树（按层序）
create tree T
build_tree T [1,2,3,#,4,#,5]
visualize T

# 保存示例（会在当前目录生成 JSON 文件）
save A "avl_saved.json"
save T "tree_saved.json"
