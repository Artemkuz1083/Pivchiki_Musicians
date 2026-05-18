import { api } from './instance'
import { SwipeAction } from '../app/types/index'
import { FullGroupProfile } from '../app/types/Group'
import { UserProfile } from '../app/types'

export const matchService = {
    // Свайп музыканта
    async swipeUser(targetUserId: number, action: SwipeAction) {
        const { data } = await api.post(`/profile/feed/${targetUserId}/swipe`, {
            action,
        })
        return data
    },

    //Мэтчи с музыкантами
    async getMatches(): Promise<UserProfile[]> {
        const { data } = await api.get('/profile/matches')
        return data
    },

    //Мэтчи с группами
    async getGroupMatches(): Promise<FullGroupProfile[]> {
        const { data } = await api.get<FullGroupProfile[]>('/groups/matches')
        return data
    }
}