from oneibl.one import ONE

one = ONE()

# query sessions that have histology available
ses = one.alyx.rest('sessions', 'list', histology=True)
# the generic way
ses = one.alyx.rest('sessions', 'list',
                    django="subject__actions_sessions__procedures__name,Histology")

# query sessions having specific channel locations (hierarchical, will fetch everything below)
ses = one.alyx.rest('sessions', 'list', atlas_id=500)
ses = one.alyx.rest('sessions', 'list', atlas_acronym="MO")
ses = one.alyx.rest('sessions', 'list', atlas_name="Somatomotor areas")


# query sessions that do not have matlab in the project name
ses = one.alyx.rest('sessions', 'list', django='~project__name__icontains,matlab')

# query sessions that do not contain a given dataset type
ses = one.alyx.rest('sessions', 'list',
                    django='~data_dataset_session_related__dataset_type__name__icontains,wheel')