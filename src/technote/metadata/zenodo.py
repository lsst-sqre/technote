"""Zenodo API support and controlled vocabularies."""

from __future__ import annotations

from enum import Enum

__all__ = ["ZenodoRole"]


class ZenodoRole(str, Enum):
    """The role of a contributor in a Zenodo record."""

    ContactPerson = "ContactPerson"
    DataCollector = "DataCollector"
    DataCurator = "DataCurator"
    DataManager = "DataManager"
    Distributor = "Distributor"
    Editor = "Editor"
    Funder = "Funder"
    HostingInstitution = "HostingInstitution"
    Producer = "Producer"
    ProjectLeader = "ProjectLeader"
    ProjectManager = "ProjectManager"
    ProjectMember = "ProjectMember"
    RegistrationAgency = "RegistrationAgency"
    RegistrationAuthority = "RegistrationAuthority"
    RelatedPerson = "RelatedPerson"
    Researcher = "Researcher"
    ResearchGroup = "ResearchGroup"
    RightsHolder = "RightsHolder"
    Supervisor = "Supervisor"
    Sponsor = "Sponsor"
    WorkPackageLeader = "WorkPackageLeader"
    Other = "Other"
