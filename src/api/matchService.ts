import { api } from './instance'
import { SwipeAction } from '../app/types/index'

export const matchService = {
	async swipeUser(targetUserId: number, action: SwipeAction) {
		const { data } = await api.post(`/profile/feed/${targetUserId}/swipe`, {
			action,
		})

		return data
	},

	async getMatches() {
		const { data } = await api.get('/profile/matches')
		return data
	},
}
