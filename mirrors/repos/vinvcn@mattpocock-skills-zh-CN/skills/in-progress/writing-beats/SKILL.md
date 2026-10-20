---
name: writing-beats
description: Writing, exploit——把原始素材组装成一段节拍旅程，在某个 beat 依赖一个术语之前先把它 grounded。
disable-model-invocation: true
---

<what-to-do>

用户已经传入（或将传入）一份 raw material markdown 文件。这是 **exploit**：探索已经完成，pile 已固定——承诺一条穿过它的路径，并挖掘 pile 来填充每个 beat。

如果用户没有说明文章保存路径，只询问一次并记住路径。

然后以自选路径（choose-your-own-adventure）风格运行 beat-by-beat journey：

1. **Establish the prerequisites.** 在任何 beat 之前，先与用户确定受众进场时已经知道什么——那些从一开始就已 **grounded** 的概念。其它一切都必须先被某个 beat grounded，之后的 beat 才能使用它。见 [Grounding](#grounding)。
2. 从 raw material 中写出 2-3 个候选 **starting beats**。每个都是进入文章的不同入口。每个都只能依赖已 grounded 的概念；记下每个 beat 新 grounded 了哪些概念。在写入文章文件之前先把这些 beats 展示给用户。用户选一个。预览选定这个 beat 后会解锁哪些 beats——就像让用户先看到路径前方一点点。
3. 用户选定 starting beat 后，只把**那个 beat**写入文章文件。一个 beat 可以是一句话，也可以是几段，按它自然需要的长度来。写完就停。
4. 从磁盘重新读取文章文件。然后提供 2-3 个候选 **next beats**——也就是从文章当前所在位置，journey 可以 pivot 的不同方向。每个都必须能从当前已 grounded 的集合到达；记下每个 beat grounded 了什么。
5. 循环步骤 3-5，直到文章自然结束。

</what-to-do>

<supporting-info>

## Grounding

每个 **concept** 都必须先被 **grounded**，某个 beat 才能依赖它：受众要么进场时就知道它，要么在更早的 beat 中遇到过它。一个伸手去抓未 grounded 概念的 beat 会失去读者——这是 journey 唯一不能做的动作。单位是 concept，而不是它的措辞：即便眼前没有任何术语，一个 beat 也可能依赖一个读者并不具备的 idea。当一个概念有名字——一个 **term**——grounded 它意味着让这个 idea 和这个 term 一起落地。

一个概念通过两种方式之一被 grounded：

- **Prerequisite** —— 在第一个 beat 之前就被 grounded。受众自带它。在开头就固定下来。
- **Introduced** —— 某个 beat 建立它，从那时起它对之后每个 beat 都是 grounded 的。

所以每个 beat 都做两件事：它**需要**已经 grounded 的概念，并 **grounds** 新的概念。维护一份到目前为止已 grounded 内容的清单，并在每个 beat 落地时更新它。

这正是塑造 choose-your-own-adventure 的东西。一个候选 beat 只有在它所需要的一切都已 grounded 时才可到达；选择一个 grounded 了概念 X 的 beat，会解锁所有在等待 X 的 beats。当你提供 next beats 时，它们都必须能从当前已 grounded 的集合到达——并说明每个 grounded 了什么，这样用户就能看到它打开了哪些路径。

关键的杠杆在于你把什么设为 prerequisite、把什么在文章内部 grounded。开头要求太多，就会把不具备这些的读者拒之门外；内部 grounded 太多，早期的 beats 就会淹没在定义里。在你确立 prerequisites 时与用户确定这一点，并且每当某个诱人的 beat 结果需要一个尚无任何东西 grounded 过的概念时就重新审视——解决办法要么是在它之前放一个 grounding beat，要么是把该概念提升为 prerequisite。

## What is a beat

Beat 是 journey 中的一步。它只做一件事：设定场景、落下一个观点、提出问题、插入 aside、扭转角度。然后停下，把读者留在一个下一个 beat 可以 pivot 的位置。

Beat 的大小由它需要完成的动作决定：

- 如果动作只有一句话，那就是一句话（"And then nothing happened for three weeks."）。
- 如果需要 setup，就是一个短段落。
- 如果 beat 是自洽的 vignette、argument 或 example，可以是多段。

如果一个 “beat” 需要五段和三个 subheadings，它就不是 beat，而是两个粘在一起的 beats。拆开。

## Pulling from the pile

从 raw pile 中抽取 material 来填充每个 beat。你可以 paraphrase、split、recombine 或 quote。这个 pile 是 quarry。

## Ending the journey

文章在 journey 完成时结束，不是在 pile 用完时结束。大多数 piles 都会剩下没有用进去的 fragments。这没关系；raw material 多于实际需要正是重点。

## Writing rhythm

- 一次追加一个 beat。永远不要提前写。
- 每次写入前都从磁盘重新读取文章文件。绝对保留用户 edits。
- 如果用户大幅编辑了之前的 beat，让它改变接下来要写什么。
- 如果用户说 "rewrite that beat" 或 "go back and try a different beat 3"，照做：就地编辑，别动其余部分。

</supporting-info>
