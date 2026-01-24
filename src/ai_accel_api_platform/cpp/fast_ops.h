#pragma once

#include <vector>

std::vector<float> batch_cosine_similarity(
    const std::vector<float>& query,
    const std::vector<std::vector<float>>& items);
