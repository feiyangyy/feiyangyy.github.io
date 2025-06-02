#include <string>
#include <vector>
#include <algorithm>
#include <assert.h>
#include <iostream>
#include <random>

std::string generate_random_string(size_t length) {
    const std::string charset =
        "0123456789"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz";
    
    static std::mt19937 rng(std::random_device{}()); // 线程安全随机数引擎
    static std::uniform_int_distribution<> dist(0, charset.size() - 1);

    std::string result;
    result.reserve(length);
    for (size_t i = 0; i < length; ++i) {
        result += charset[dist(rng)];
    }
    return result;
}

// 生成字符串数组
std::vector<std::string> generate_random_string_array(size_t count, size_t string_length) {
    std::vector<std::string> result;
    result.reserve(count);
    for (size_t i = 0; i < count; ++i) {
        result.push_back(generate_random_string(string_length));
    }
    return result;
}


void DoCountString(std::vector<std::string>& strs, std::vector<int> keys, int max_key) {
    std::vector<std::string> aux;
    std::vector<int> key_counters;
    aux = std::vector<std::string> (strs.size());
    key_counters = std::vector<int> (max_key + 1, 0);
    // count the frequecy
    for(const auto& key: keys) {
        // key_counters[0] = 0;
        key_counters[key + 1]++;
    }
    // change the frequency to the index
    // 这里成立的条件是，k[i+1]_s = k[i]_s + k[i].len(); => 非常简单的动归算法 
    // k[i+1]_s = k[i-1]_s + k[i-1].len() + k[i].len() 
    // = .. = k[0]_s + sum(k[i].len());
    // 这里的count[i] = k[i-1].len();
    std::vector<int> key_indcies = std::vector<int> (key_counters.size(), 0);

    std::vector<int> key_counter_copy = key_counters;

    for (int ks = 0; ks < max_key; ks++) {
        // k_i[min + 1] = 0 + k_i[min] => k_i[min + 1] 第二个key的start_index
        // k_i[min + 2] = k_i[min + 1] + k_i[min]
        key_indcies[ks + 1] = key_indcies[ks] + key_counters[ks + 1];
    }

    for(int ks = 0; ks < max_key; ks++) {
        // 这里的ks是key的index
        // 这里的key_counter_copy[ks]是key的长度
        // 这里的key_indcies[ks]是key的start_index
        key_counter_copy[ks + 1] = key_counter_copy[ks] + key_counter_copy[ks + 1];
    }
    assert(std::equal(key_counter_copy.begin(), key_counter_copy.end(), key_indcies.begin()));

    // traverse all the keys, and write down the strs in to the aux
    int sz = static_cast<int>(keys.size());
    for (int i = 0; i < sz; ++i) {
        // 相当于一个index数组，并且chunk内，index 都是相同的
        aux[key_indcies[keys[i]]++] = strs[i];
    }
    // 写回
    for (int i = 0; i < sz; ++i) {
        strs[i] = aux[i];
    }
}


// LSD低位排序
struct LSD {
    static constexpr int KEY_MAX=255;
    std::vector<std::string> aux;
    // 某些平台好像会实现成unsigned char
    std::vector<int> key_counters_;
    // to make it clear, but not necessarys
    std::vector<int> key_indcies_;
    // 注意LSD的核心思想，从右往左，然后按照ith 的char 进行计数排序，直到完成操作
    // LSD 限制，所有字符串必须等长

    void DoLSD(std::vector<std::string>& inputs) {
        int sz = inputs.size();
        aux.resize(sz);
        key_counters_ = std::vector<int>(KEY_MAX + 1, 0);
        key_indcies_ = key_counters_;
        int str_len = static_cast<int>  (inputs[0].size());
        // 每次都要重做计数
        for (int ci = str_len - 1; ci >= 0; --ci) {
            // key_counters_.assign(key_counters_.size(), 0);
            std::fill(key_counters_.begin(), key_counters_.end(), 0);
            // bad idea.
            // key_indcies_ = key_counters_;
            std::fill(key_indcies_.begin(), key_indcies_.end(), 0);
            // 计数
            for(const auto& s: inputs) {
                // 记得下面的递推公式
                ++key_counters_[s[ci] + 1];
            }
            // 转为索引
            for (int ks = 0; ks < KEY_MAX; ++ks) {
                // 仍然,key_counters[ks + 1] = key_chunk[ks].len();
                key_indcies_[ks + 1] = key_indcies_[ks] + key_counters_[ks + 1];
            }
            // 调整顺序
            // 这里要注意，输入是乱序的，因此s[ci] 所得到的index 是跳变的
            // 这里是把s按照key的顺序，写到指定chunk
            for (const auto& s: inputs) {
                aux[key_indcies_[s[ci]]++] = s;
            }
            // 写回
            for (int i = 0; i < sz; ++i) {
                inputs[i] = aux[i];
            }
        }
    }
};

// MSD高位排序

void print_strings(const std::vector<std::string>& strs) {
    for(const auto& s:strs) {
        std::cout << s << " ";
    }
    std::cout << std::endl;
}


int main() {
    std::vector<std::string> strs = {"c", "a", "d", "a", "f", "g", "h", "a", "e"};
    std::vector<int> keys;
    for(const auto& s:strs) {
        keys.emplace_back(static_cast<int> (s[0]));
    }
    DoCountString(strs, keys, 255);
    print_strings(strs);
    strs = {"c", "a", "d", "a", "f", "g", "h", "a", "e"};
    LSD lsd;
    lsd.DoLSD(strs);
    print_strings(strs);
    
    std::vector<std::string> strs2 = generate_random_string_array(100, 10);
    lsd.DoLSD(strs2);
    print_strings(strs2);
    return 0;
}