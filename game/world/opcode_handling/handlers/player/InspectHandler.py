from struct import unpack

from game.world.managers.objects.units.player.PlayerManager import PlayerManager
from game.world.managers.maps.MapManager import MapManager
from game.world.opcode_handling.HandlerValidator import HandlerValidator
from network.packet.PacketReader import PacketReader
from network.packet.PacketWriter import *


class InspectHandler(object):

    @staticmethod
    def handle(world_session, socket, reader: PacketReader) -> int:
        # Validate world session.
        player_mgr, res = HandlerValidator.validate_session(world_session, reader.opcode, disconnect=True)
        if not player_mgr:
            return res

        if len(reader.data) >= 8:  # Avoid handling empty inspect packet.
            guid = unpack('<Q', reader.data[:8])[0]
            if guid > 0:
                inspected_player: PlayerManager = MapManager.get_surrounding_player_by_guid(player_mgr, guid)
                if not inspected_player or not inspected_player.is_alive:
                    return 0

                player_mgr.set_current_selection(guid)
                data = pack('<Q', player_mgr.guid)
                inspected_player.enqueue_packet(PacketWriter.get_packet(OpCode.SMSG_INSPECT, data))

        return 0
