#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "fast_ops.h"

namespace py = pybind11;

PYBIND11_MODULE(fast_ops, m) {
    m.doc() = "Fast ops for cosine similarity";
    m.def(
        "batch_cosine_similarity",
        &batch_cosine_similarity,
        "Compute cosine similarity for a batch of vectors",
        py::arg("query"),
        py::arg("items"));
}
