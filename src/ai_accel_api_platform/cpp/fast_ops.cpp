#include "fast_ops.h"

#include <algorithm>
#include <cmath>

std::vector<float> batch_cosine_similarity(
    const std::vector<float>& query,
    const std::vector<std::vector<float>>& items) {
    std::vector<float> scores;
    scores.resize(items.size(), 0.0f);

    float query_norm = 0.0f;
    for (float v : query) {
        query_norm += v * v;
    }
    query_norm = std::sqrt(query_norm) + 1e-8f;

#ifdef USE_OPENMP
#pragma omp parallel for
#endif
    for (size_t i = 0; i < items.size(); ++i) {
        const auto& item = items[i];
        float dot = 0.0f;
        float item_norm = 0.0f;
        size_t dim = std::min(query.size(), item.size());
        for (size_t j = 0; j < dim; ++j) {
            dot += query[j] * item[j];
            item_norm += item[j] * item[j];
        }
        item_norm = std::sqrt(item_norm) + 1e-8f;
        scores[i] = dot / (query_norm * item_norm);
    }

    return scores;
}
