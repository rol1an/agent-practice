# Agent Practice · 与 Agent 一起把事情想清楚、做扎实

彭罗健 · 持续更新

这里记录我在真实工作中使用 Agent 的思考，并把可复用的方法整理成可下载的 Skills。第一组材料来自一次论文改稿与组会分享，后续会继续收录其他场景的实践。

**认知卸载，而非认知投降：让 Agent 分担执行，人仍对问题、证据与取舍负责。**

## 先用哪个 Skill？

| 你现在遇到的问题 | Skill | 交付 |
|---|---|---|
| 材料散乱、不知道哪版是当前稿、结果追不到数据 | [research-materials：科研材料整理](skills/research-materials/SKILL.md) | 可追溯的目录/索引、版本关系、缺件清单 |
| 有材料，但说不清研究问题、主线或下一步 | [research-thinking：科研思考与协作](skills/research-thinking/SKILL.md) | 有依据的逐轮提问、研究决策卡、可核验的下一步 |

两个 Skill 独立可用。材料齐全时直接讨论研究；讨论发现缺件，再补材料。简单改图和格式任务不必先做一轮科研访谈。

```text
材料与版本清楚 → 问题与证据清楚 → 执行和复核 → 方法可被下一位同学复用
     ↑                    │                              │
     └──── 发现缺口、补材料 ┴────────── 持续改进 ──────────┘
```

## 下载与开始使用

点击 GitHub 的 **Code → Download ZIP**，解压后保留 `skills/` 下所需 Skill 的完整文件夹，包括 `references/`、`scripts/` 和 `agents/`。也可以：

```sh
git clone https://github.com/rol1an/agent-practice.git
```

如果你的 Agent 支持从仓库安装 Skill，可以让它安装本仓库的 `skills/research-materials` 和 `skills/research-thinking` 两个目录。Codex 的 Skill Installer 可以按这两个仓库路径安装；安装完成后在下一轮使用。

不同客户端的自动发现目录可能不同，以所在客户端的规则为准。尚未安装时，也可以在有本地文件读取能力的 Codex / Claude Code 会话中直接说：

> 阅读 `agent-practice/skills/research-materials/SKILL.md`，按其中方法盘点我指定的研究目录；先识别当前稿、来源和缺件，不覆盖原始文件。

> 阅读 `agent-practice/skills/research-thinking/SKILL.md`，先读我提供的原稿、前作与导师意见，再问我一个最影响下一步判断的问题。

安装并被宿主识别后，可按该客户端的 Skill 调用方式使用 `research-materials` / `research-thinking`。Skill 是给 Agent 的指令文件；它本身不包含模型服务，不会因为下载就自动执行。建议用一份小型项目副本先试。

材料盘点脚本只需 Python 3 标准库：

```sh
python3 skills/research-materials/scripts/inventory.py /path/to/paper
# 需要核对字节重复时再计算哈希
python3 skills/research-materials/scripts/inventory.py /path/to/paper --hash
```

## 我想保留下来的思考

- [认知卸载、判断与导师视角](notes/01-cognitive-offloading.md)
- [文件树为什么也是科研协作的一部分](notes/02-research-context.md)
- [接下来继续验证什么](ROADMAP.md)

这些来自有限实践，是待检验的方法，不是论文质量或效率提升的保证。材料目录整齐不等于推理正确；两个模型意见一致不等于结果已经验证。

## 当前版本与验证范围

初版包含两个 Skill、一个只读材料盘点脚本，以及 [试用场景](evals/scenarios.json)。脚本的自动测试见 `tests/test_inventory.py`；Skill 的提问质量需要在真实研究任务中继续评估，未宣称跨模型效果已验证。

运行脚本测试：

```sh
python3 -m unittest discover -s tests -v
```

## 后续怎样积累

新想法先作为 `notes/` 中的观察记录，写清场景、做法、证据、失败和适用边界；重复出现且有稳定做法后，再整理成独立 Skill。欢迎通过 Issue 分享去除隐私后的使用案例，不要提交原始研究数据、未发表稿件、私人通信或访问凭据。

本仓库只发布方法与抽象案例，不包含论文原稿、导师回信、工作内部资料、照片或他人论文全文。作者：彭罗健。采用 [MIT License](LICENSE)，可复制、修改与分发，并保留许可声明。
