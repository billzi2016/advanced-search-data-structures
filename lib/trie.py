from dataclasses import dataclass, field


@dataclass
class _TrieNode:
    children: dict[str, "_TrieNode"] = field(default_factory=dict)
    is_word: bool = False


class Trie:
    def __init__(self) -> None:
        # 根节点不对应任何字符，只作为所有字符串的公共入口。
        self.root = _TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for char in word:
            # 如果当前字符路径不存在，就创建新节点。
            node = node.children.setdefault(char, _TrieNode())
        # 只有末尾节点标记为单词，前缀本身不一定是完整单词。
        node.is_word = True

    def contains(self, word: str) -> bool:
        # 先走完整路径，再确认末尾是否被标记为单词。
        node = self._walk(word)
        return node is not None and node.is_word

    def starts_with(self, prefix: str) -> bool:
        # 前缀只要求路径存在，不要求末尾是完整单词。
        return self._walk(prefix) is not None

    def delete(self, word: str) -> None:
        # 删除后会递归清理不再被其他单词共享的无用节点。
        self._delete(self.root, word, 0)

    def words_with_prefix(self, prefix: str) -> list[str]:
        # 先定位前缀末尾节点，再从该节点收集所有后缀。
        node = self._walk(prefix)
        if node is None:
            return []

        result: list[str] = []
        self._collect(node, prefix, result)
        return result

    def _walk(self, text: str) -> _TrieNode | None:
        node = self.root
        for char in text:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def _delete(self, node: _TrieNode, word: str, index: int) -> bool:
        if index == len(word):
            if not node.is_word:
                return False
            # 取消单词标记；如果没有孩子，通知父节点可以剪枝。
            node.is_word = False
            return not node.children

        char = word[index]
        child = node.children.get(char)
        if child is None:
            return False

        should_prune = self._delete(child, word, index + 1)
        if should_prune:
            # 子树已经没有单词经过，可以删除该字符边。
            del node.children[char]

        # 当前节点如果既不是单词结尾，也没有孩子，也可以继续向上剪枝。
        return not node.is_word and not node.children

    def _collect(self, node: _TrieNode, prefix: str, result: list[str]) -> None:
        if node.is_word:
            result.append(prefix)

        # 排序遍历子节点，保证输出结果稳定可复现。
        for char in sorted(node.children):
            self._collect(node.children[char], prefix + char, result)
