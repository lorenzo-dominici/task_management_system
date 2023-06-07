# Task Management System

this django project has been developed for the purpose of the course of *Progettazione e Produzione Multimediale* as a part of the *Laurea in Ingegneria Informatica* at the *Università degli Studi di Firenze*

## Notes

For the purpose of this course, the project has not been developed to completion. Here follow some feature not implemented:
- search
- pagination
- filters
- ordering
- some managing operations
- some functionalities

Furthermore, the project does not implement several mechanisms to increase its efficiency, such as the `select_related()` method that lessen the load on the database.

## Functionalities
Here are described the implemented features:
- A `user` can create a `project`, becoming its owner.
- A *project owner* can create a `role` in its project.
- A *project owner* can create a `task` in its project, restricted to some project roles.
- A *project owner* can edit its `project`, the project `role`s and the project `task`s.
- A *project owner* can `invite` another user to join its `project` under a specific `role`, making it a project *collaborator*.
- A *project owner* can accept or reject a request to join its project under a specific role, sent by another `user`.
- A `user` can request a *project owner* to join its `project` under a specific `role`, making itself a project *collaborator*.
- A `user` can accept or reject an invitation to join its project under a specific role, sent by a *project owner*.
- Both a *project owner* and a *collaborator* can revoke an invitation/request sent before it has been accepted or rejected by the receiver.
- A *project owner* can assign a `role` to a *collaborator*.
- A *project owner* can dismiss a *collaborator* from one of its `role`s.
- A *collaborator* is competent in a specific `task` only if it has at least a `role` in common with the `task` requirements.
- A *project owner* can assign a `task` to a competent *collaborator*.
- A *project owner* can revoke a `task` from a competent *collaborator*.
- A *collaborator* can claim a `task` in which it is competent.
- A *collaborator* can leave a `task` assigned to it.
- A *collaborator* can start a `task` assigned to it.
- A *collaborator* can end a `task` assigned to it.
- A *project owner* can accept or reject a `task` ended by a *collaborator*.

For the purpose of maintaining knowledge integrity, the only *delete* operation implemented is in the "revoke invitation/request" feature, and other *editing* operations are restricted to non-final states, to avoid data chnages after completion. These inner policies are not essential in a fair or controlled user environment, but grants consistency to the system.