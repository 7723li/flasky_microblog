Flasky
======

This repository contains the source code examples for my O'Reilly book [Flask Web Development](http://www.flaskbook.com).

The commits and tags in this repository were carefully created to match the sequence in which concepts are presented in the book. Please read the section titled "How to Work with the Example Code" in the book's preface for instructions.

严格来说， ForgeryPy 并不是这个程序的依赖，因为它只在开发过程中使用。为了区分生
产环境的依赖和开发环境的依赖， 我们可以把文件 requirements.txt 换成 requirements 文件
夹，它们分别保存不同环境中的依赖。 在这个新建的文件夹中，我们可以创建一个 dev.txt
文件，列出开发过程中所需的依赖，再创建一个 prod.txt 文件，列出生产环境所需的依赖。
由于两个环境所需的依赖大部分是相同的， 因此可以创建一个 common.txt 文件，在 dev.txt
和 prod.txt 中使用 -r 参数导入

示例 11-7 requirements/dev.txt：开发所需的依赖文件
-r common.txt
ForgeryPy==0.1