# Ignareo

基于 Python 的高性能世萌自动投票器。

可在 4GHz Ryzen 3600 core 上达到 0.7 秒 100000 次请求的性能

## 运行环境

Ignareo 支持的最低版本是 Python 3.6，推荐版本为 Python 3.7。

**注意：对于 Windows 上的 Python 3.8 用户，您可能需要增加这些代码解决 `NotImplementedError`。**

```python3
import platform  
if platform.system() == "Windows":  
    import asyncio  
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  
```

## 上手教程

Ignareo 目前仍是一个骨架，但它和其他库（例如`scrapy`）是本质不同的。我们**不会发布** Ignareo 的 API 化版本。

若您想要按照您的需求重构 Ignareo，请先阅读 `DestroyerIGN/IgnareoG.py` 以了解项目的架构。

若您想要直接使用，则本 README 的剩余部分将带您理解源代码和使用方法。

## 如何在世萌中用 Ignareo 进行投票

这是 Ignareo 项目的本意，即使您不需要这一功能，也不妨一读。

### 如何开始投票？

在 `./DestroyerIGN` 中，首先运行 `captchaServer.py`，接着运行 `IgnareoG.py`，最后运行 `Ammunition.py` 来给 Ignareo 提供弹药（代理）。




