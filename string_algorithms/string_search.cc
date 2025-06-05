#include <string>
#include <vector>
#include <iostream>

struct Tries {
    static constexpr int R=256;
    int32_t val = -1;
    char key = 0;
    std::vector<Tries*> children;
    Tries() : children(R, nullptr) {}

    static Tries* put(Tries* node, const std::string& key, int val, int depth = 0) {
        if(depth > key.size()) {
            return nullptr;
        }
        if (!node) {
            node = new Tries();
        }
        // key 暗含在数组中，其实不需要了
        node->key = key[depth - 1];
        // 到达末尾
        if(depth == key.size()) {
            node->val = val;
            return node;
        }
        // 继续迭代
        node->children[node->key] = put(node->children[node->key], key, val, depth + 1);
        return node;
    }

    static uint32_t size(Tries* node) {
        uint32_t res = 0;
        size(node, 0 ,res);
        return res;
    }

    static bool find(Tries* node, const std::string& key, int depth = 0) {
        if (!node) {
            return false;
        }
        if (depth == key.size()) {
            // 长度相等时，检查节点值
            return node->val != -1;
        }
        // 递归， 下一层的key是key[depth]
        return find(node->children[key[depth]], key, depth + 1);
    }
private:
    static void size(Tries* node, int depth, uint32_t& res) {
        if (!node) {
            return;
        }
        if (node->val != -1) {
            res += 1;
        }
        for(int i = 0; i < R; i++) {
            size(node->children[i], depth + 1, res);
        }
    }
};