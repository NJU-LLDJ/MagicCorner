# 后端开发文档

## 使用语言

考虑到`Python 3.12`刚刚发布一个月，许多第三方库仍未适配，因此采用`Python 3.11`作为后端开发的语言。

请使用虚拟环境（如`venv`,`conda`）隔离开发环境，避免版本冲突。

## 使用框架

1. [FastAPI](https://fastapi.tiangolo.com/tutorial/)
2. [Pydantic](https://docs.pydantic.dev/latest/)

其中，`FastAPI`提供了web框架，`Pydantic`帮助我们创建数据模型。

## 代码规范

### 参考文档

1. [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
2. [PEP 484 – Type Hints](https://peps.python.org/pep-0484/)
3. [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
4. [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines)

### 具体要求

> 以下加粗的限定词参见[RFC 2119: Key words for use in RFCs to Indicate Requirement Levels](https://www.rfc-editor.org/rfc/rfc2119)

- 你**必须**根据`PEP 8`命名类、函数、方法、变量等。
- 你**必须**根据`PEP 484`为每一个函数、方法的参数及返回值标注类型。
- 你**应该**根据`PEP 484`以及实际情况为某些模棱两可的变量标注类型，包括但不限于：
  - 变量保存了函数返回值，而该函数没有标注返回值类型
  - 变量类型与直觉不符的（也许你应该修改变量名？）
  - 其它导致IDE不能自动推断出变量类型的情况
- 你**可以**根据`Google Python Style Guide`编写代码。
- 你**必须**根据`REST API`设计API的路径。
- 你**必须**将代码正确格式化以后再上传。
- 你**必须**为每一个函数、方法编写文档（`docstring`），函数、方法内部**可以**没有注释，但是其行为**必须**与文档保持一致。
- 你**应该**异步`async`地处理网络IO，数据库请求等通信耗时任务。
- 你**不允许**将密码等敏感信息硬编码进代码中。
