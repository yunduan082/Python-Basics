# Abaqus 2025 三点弯曲试验 Plugin（Python 3）

该仓库提供了一个可直接放入 Abaqus/CAE 的插件骨架，用于快速创建三点弯曲试样几何体。

## 目录结构

- `three_point_bending_plugin/three_point_bending_plugin.py`：GUI 表单与菜单注册。
- `three_point_bending_plugin/tpb_kernel.py`：Kernel 侧建模函数。
- `three_point_bending_plugin/abaqus_plugin.py`：Abaqus 插件加载入口。

## 安装

1. 将 `three_point_bending_plugin` 文件夹复制到 Abaqus 插件目录，例如：
   - Windows: `%APPDATA%\DassaultSystemes\Abaqus\Plugins\2025\`
   - Linux: `~/.abaqus_plugins/`
2. 重启 Abaqus/CAE。
3. 在 `Plug-ins` 菜单中找到 `Three-Point Bending...`。

## 当前功能

- 输入试样长度、宽度、高度。
- 输入支撑跨度与压头半径（当前版本先保存参数，后续可扩展接触/分析步/加载）。
- 在 `Model-1` 中创建（或覆盖）`Specimen` 三维实体。

## 后续扩展建议

- 自动创建两个支撑辊和上压头的离散刚体。
- 自动建立接触属性与接触对。
- 自动创建 Static, General 步、位移加载、输出请求。
- 参数化网格划分策略与单元类型（如 C3D8R）。
