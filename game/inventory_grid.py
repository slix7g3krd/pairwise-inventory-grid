"""第 54 批：背包网格系统。

修复点：
- 像素坐标 -> 格子坐标用整除换算，不再按像素直接比较；
- 旋转时交换宽高；
- 堆叠上限按物品类型区分（装备类不可堆叠，其余用基础上限）；
- 拖拽放置前检查边界与碰撞；
- 扩容后按偏移量迁移旧坐标；
- 拆分只产生整数并做范围夹取；
- 排序键统一小写，保证大小写不敏感的稳定排序；
- 空格搜索从左上扫描且跳过已占格；
- 卸下装备时释放占位并返回是否真正释放；
- 网络同步时本地预测优先。
"""

# 装备类物品不可堆叠，任何基础上限都被压到 1。
NON_STACKABLE_TYPES = frozenset({
    "weapon",
    "armor",
    "shield",
    "helmet",
    "boots",
    "gloves",
    "accessory",
    "ring",
    "amulet",
    "tool",
    "equipment",
})


def cell_coord(x, y, cell_size):
    """把像素坐标换算为格子坐标（整除，逐格 cell_size 像素）。"""
    if cell_size <= 0:
        raise ValueError("cell_size must be positive")
    return (x // cell_size, y // cell_size)


def rotate_size(width, height, rotated):
    """旋转后交换物品宽高；未旋转时原样返回。"""
    if rotated:
        return (height, width)
    return (width, height)


def stack_limit(item_type, base_limit):
    """返回按物品类型的堆叠上限。

    装备/武器/护甲等不可堆叠类型固定为 1；
    药水、材料等可堆叠类型使用调用方给出的基础上限。
    """
    if item_type in NON_STACKABLE_TYPES:
        return 1
    if not isinstance(base_limit, int) or base_limit < 1:
        return 1
    return base_limit


def can_place(grid, x, y, width, height):
    """检查拖拽占格是否碰撞：目标矩形必须完全在网格内且每格都为空。"""
    if width <= 0 or height <= 0:
        return False

    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    if y < 0 or x < 0 or y + height > rows or x + width > cols:
        return False

    for row in range(y, y + height):
        for col in range(x, x + width):
            if grid[row][col]:
                return False
    return True


def migrate(position, offset):
    """扩容后迁移旧坐标：位置与偏移量逐分量相加。"""
    return (position[0] + offset[0], position[1] + offset[1])


def split_count(count, amount):
    """整数拆分堆叠数量，返回 (拆出数量, 剩余数量)。

    amount 被夹取到 [0, count]，不会出现小数或负数。
    """
    amount = max(0, min(int(count), int(amount)))
    return (amount, int(count) - amount)


def sort_key(item):
    """返回稳定排序键：名称统一转小写，实现大小写不敏感排序。"""
    if isinstance(item, dict):
        item = item.get("name", "")
    return str(item).lower()


def find_slot(grid, width, height):
    """从左上查找可用空格，扫描时跳过所有已占格；找不到返回 None。"""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    for y in range(rows):
        for x in range(cols):
            if can_place(grid, x, y, width, height):
                return (x, y)
    return None


def release_slot(occupied, x, y):
    """卸下装备时释放占位。

    目标格原本被占用则清空并返回 True；本来就是空格或坐标越界则返回 False。
    """
    if y < 0 or x < 0 or y >= len(occupied):
        return False
    row = occupied[y]
    if x >= len(row):
        return False
    if not row[x]:
        return False
    row[x] = 0
    return True


def reconcile(local, remote):
    """返回本地预测优先的同步结果。

    - 本地有预测状态时一律以本地为准，避免网络回包覆盖进行中的拖拽；
    - 本地为空（None）时回退到远端状态；
    - 两边都是字典时以远端为底、本地字段覆盖合并。
    """
    if local is None:
        return remote
    if isinstance(local, dict) and isinstance(remote, dict):
        merged = dict(remote)
        merged.update(local)
        return merged
    return local
