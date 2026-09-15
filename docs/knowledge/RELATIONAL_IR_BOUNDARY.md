# Local / relational geometry boundary

`rqm-core` owns local quaternion algebra, unit-quaternion/SU(2) conventions, spinors, and single-qubit geometry.

`rqm-entanglement` owns two-qubit relational representations and their exact conventional materialization: `BellHinge`, `AxisHinge`, `CartanRelation`, and `QuaternionCartanBlock`, including promotion/demotion and composition mathematics.

`rqm-compiler` may consume those types for recognition and routing but must not fork their canonical mathematics into core. The ecosystem principle is to use the smallest exact representation justified by structure and promote only when closure is lost.
