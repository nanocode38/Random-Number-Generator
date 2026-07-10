# 测试说明

本项目使用 pytest 框架进行单元测试。

## 依赖要求

运行测试需要安装以下依赖（项目本身不包含这些测试依赖）：

```bash
pip install pytest pytest-mock
```

或者如果使用 uv：

```bash
uv add --dev pytest pytest-mock
```

## 运行测试

### 运行所有测试
```bash
pytest test/
```

### 运行特定测试文件
```bash
pytest test/test_tools.py
pytest test/test_picker.py
pytest test/test_constant.py
```

### 运行特定测试类或方法
```bash
pytest test/test_tools.py::TestLoadSettings
pytest test/test_tools.py::TestLoadSettings::test_load_settings_success
```

### 查看详细输出
```bash
pytest test/ -v
```

### 显示打印输出
```bash
pytest test/ -s
```

### 生成覆盖率报告
首先需要安装 pytest-cov：
```bash
pip install pytest-cov
```

然后运行：
```bash
pytest test/ --cov=src --cov-report=html
```

## 测试文件说明

- `conftest.py` - pytest 配置和共享 fixtures
- `test_tools.py` - 测试工具函数（设置管理、重启等）
- `test_picker.py` - 测试学生选择器核心逻辑
- `test_constant.py` - 测试常量配置和路径

## 注意事项

1. **GUI 测试限制**：由于 PySide6 GUI 组件需要图形环境，大部分测试通过 mock 对象来避免实际 GUI 初始化。

2. **临时文件**：测试使用临时目录，测试完成后自动清理，不会影响项目实际数据。

3. **导入方式**：测试中使用绝对导入 `from src.xxx import ...`，确保从项目根目录运行测试。

4. **Mock 策略**：
   - QApplication 和 GUI 组件被 mock
   - 文件系统操作使用临时目录
   - 外部依赖（如 subprocess）被 mock

## 编写新测试

添加新测试时请遵循以下规范：

1. 测试文件放在 `test/` 目录下
2. 文件名以 `test_` 开头
3. 测试类名以 `Test` 开头
4. 测试方法名以 `test_` 开头
5. 使用描述性的测试名称说明测试目的
6. 每个测试方法只测试一个功能点
7. 使用 fixtures 提供测试数据和 mock 对象

示例：
```python
def test_example_function_with_valid_input(self, fixture_name):
    """Test that example function works with valid input."""
    from src.module import example_function
    
    result = example_function(valid_input)
    
    assert result == expected_output
```
