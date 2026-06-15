// pybind11 bindings for the robosim C++ core.
//
// HARD RULE (boundary discipline): this translation unit carries ZERO business
// logic. It only marshals types between Python and the core. Keeping it
// logic-free is what lets the binding library be swapped (e.g. to nanobind)
// mechanically, and avoids ownership/lifetime bugs.

#include <pybind11/eigen.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "robosim/model.hpp"
#include "robosim/system.hpp"

namespace py = pybind11;
using robosim::Model;
using robosim::System;

PYBIND11_MODULE(_core, m) {
  m.doc() = "robosim C++ core (Milestone 0: 3D point mass).";

  py::class_<Model>(m, "Model")
      .def(py::init([](double mass, double dt, Eigen::Vector3d gravity, int nq,
                       int nv) {
             Model md;
             md.mass = mass;
             md.dt = dt;
             md.gravity = std::move(gravity);
             md.nq = nq;
             md.nv = nv;
             return md;
           }),
           py::arg("mass") = 1.0, py::arg("dt") = 0.01,
           py::arg("gravity") = Eigen::Vector3d::Zero(), py::arg("nq") = 3,
           py::arg("nv") = 3)
      .def_readwrite("mass", &Model::mass)
      .def_readwrite("dt", &Model::dt)
      .def_readwrite("gravity", &Model::gravity)
      .def_readonly("nq", &Model::nq)
      .def_readonly("nv", &Model::nv);

  py::class_<System>(m, "System")
      .def(py::init<Model>(), py::arg("model"))
      .def("reset", &System::reset, py::arg("qpos"), py::arg("qvel"))
      .def("set_control", &System::set_control, py::arg("u"))
      .def("step", &System::step, py::arg("n_substeps") = 1)
      .def("seed", &System::seed, py::arg("seed"))
      .def_property_readonly("qpos", &System::qpos)
      .def_property_readonly("qvel", &System::qvel)
      .def_property_readonly("time", &System::time)
      .def_property_readonly("diverged", &System::diverged)
      .def_property_readonly("energy", &System::energy)
      .def_property_readonly(
          "model", &System::model,
          py::return_value_policy::reference_internal);
}
