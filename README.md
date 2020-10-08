# Bioschemas ProfileGenerator
Experimental scripts for creating a new Bioschemas Profile

## Installation

If you have Conda/[BioConda](https://bioconda.github.io/) the below should hopefully work:

```shell
    git clone https://github.com/BioSchemas/ProfileGenerator
    cd ProfileGenerator
    conda env create
    conda activate profilegenerator
    type python  ## /home/stain/miniconda3/envs/profilegenerator/bin/python
    python setup.py install
```

## Usage

```
conda activate profilegenerator
python setup.py install  # reinstall on code update
bioschema-profilegen -v
bioschema-profilegen -h
bioschema-profilegen Dataset FancyDataset
```

If you don't have Conda, or use virtualenv or similar, then `setup.py` lists the Python dependencies. This code has been tested with Python 3.8.

### Schema.org examples

You can show auto-generated examples for a particular schema.org property:


```shell
(profilegenerator) stain@biggie:~/src/ProfileGenerator$ schemaorg-example attendee
```

```json
{ "@context": "https://schema.org/",
  "@id": "https://example.com/event/123",
  "@type": "Event",
  "attendee": {"@id": "https://example.com/organization/345", "@type": "Organization"}
}
{ "@context": "https://schema.org/",
  "@id": "https://example.com/event/123",
  "@type": "Event",
  "attendee": {"@id": "https://orcid.org/0000-0002-1825-0097", "@type": "Person"}
}
```

The above shows one example for each each potential `@type` in the range of the property.

It is possible to generate a complete (but perhaps overwhelming) example of a given schema.org type. In this case only one potential `@type` is rendered per property:

```shell
(profilegenerator) stain@biggie:~/src/ProfileGenerator$ schemaorg-example Event
```

```json
{ "@context": "https://schema.org/",
  "@id": "https://example.com/event/123",
  "@type": "Event",
  "about": {"@id": "https://example.com/thing/345", "@type": "Thing"},
  "actor": {"@id": "https://orcid.org/0000-0002-1825-0097", "@type": "Person"},
  "aggregateRating": {"@type": "AggregateRating"},
  "attendee": {"@id": "https://orcid.org/0000-0002-1825-0097", "@type": "Person"},
  "attendees": {"@id": "https://orcid.org/0000-0002-1825-0097", "@type": "Person"},
  "audience": {"@type": "Audience"},
  "composer": {"@id": "https://orcid.org/0000-0002-1825-0097", "@type": "Person"},
  "contributor": {"@id": "https://orcid.org/0000-0002-1825-0097", "@type": "Person"},
  "director": {"@id": "https://orcid.org/0000-0002-1825-0097", "@type": "Person"},
  "doorTime": "2020-10-08T17:33:08+01:00",
  "duration": {"@type": "Duration"},
  "endDate": "2020-10-08",
  "eventAttendanceMode": {"@type": "EventAttendanceModeEnumeration"},
  "eventSchedule": {"@type": "Schedule"},
  "eventStatus": {"@type": "EventStatusType"},
  "funder": {"@id": "https://example.com/organization/345", "@type": "Organization"},
  "inLanguage": "example inlanguage",
  "isAccessibleForFree": false,
  "location": {"@id": "https://example.com/place/345", "@type": "Place"},
  "maximumAttendeeCapacity": 123,
  "maximumPhysicalAttendeeCapacity": 123,
  "maximumVirtualAttendeeCapacity": 123,
  "offers": {"@type": "Offer"},
  "organizer": {"@id": "https://example.com/organization/345", "@type": "Organization"},
  "performer": {"@id": "https://orcid.org/0000-0002-1825-0097", "@type": "Person"},
  "performers": {"@id": "https://example.com/organization/345", "@type": "Organization"},
  "previousStartDate": "2020-10-08",
  "recordedIn": {"@id": "https://example.com/creativework/345", "@type": "CreativeWork"},
  "remainingAttendeeCapacity": 123,
  "review": {"@id": "https://example.com/review/345", "@type": "Review"},
  "sponsor": {"@id": "https://orcid.org/0000-0002-1825-0097", "@type": "Person"},
  "startDate": "2020-10-08T17:33:08+01:00",
  "subEvent": {"@id": "https://example.com/event/345", "@type": "Event"},
  "subEvents": {"@id": "https://example.com/event/345", "@type": "Event"},
  "superEvent": {"@id": "https://example.com/event/345", "@type": "Event"},
  "translator": {"@id": "https://orcid.org/0000-0002-1825-0097", "@type": "Person"},
  "typicalAgeRange": "example typicalagerange",
  "workFeatured": {"@id": "https://example.com/creativework/345", "@type": "CreativeWork"},
  "workPerformed": {"@id": "https://example.com/creativework/345", "@type": "CreativeWork"},
  "additionalType": "https://purl.example.org/additionaltype-345",
  "alternateName": "example alternatename",
  "description": "example description",
  "disambiguatingDescription": "example disambiguatingdescription",
  "identifier": "https://purl.example.org/identifier-345",
  "image": "https://purl.example.org/image-345",
  "mainEntityOfPage": "https://purl.example.org/mainentityofpage-345",
  "name": "example name",
  "potentialAction": {"@id": "https://example.com/action/345", "@type": "Action"},
  "sameAs": "https://purl.example.org/sameas-345",
  "subjectOf": {"@id": "https://example.com/creativework/345", "@type": "CreativeWork"},
  "url": "https://purl.example.org/url-345"
}
```

## License

MIT License <https://spdx.org/licenses/MIT>
  
Copyright (c) 2020 Heriot-Watt University, UK  
Copyright (c) 2020 The University of Manchester, UK

See [LICENSE](LICENSE) for details.
