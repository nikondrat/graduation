import { apiFetch } from '../api/http'
import type { Photo } from '../data/photos'

export interface OrderItemData {
  id: number
  photo: Photo
  licenseType: string
  price: number
}

export interface OrderListData {
  id: number
  status: 'pending' | 'paid' | 'cancelled'
  total: number
  createdAt: string
  paidAt: string | null
  itemsCount: number
}

export interface OrderDetailData {
  id: number
  status: 'pending' | 'paid' | 'cancelled'
  total: number
  items: OrderItemData[]
  createdAt: string
  paidAt: string | null
}

export async function getOrders(): Promise<OrderListData[]> {
  return apiFetch<OrderListData[]>('/orders/')
}

export async function getOrder(id: number): Promise<OrderDetailData> {
  return apiFetch<OrderDetailData>(`/orders/${id}/`)
}

export async function payOrder(id: number): Promise<OrderDetailData> {
  return apiFetch<OrderDetailData>(`/orders/${id}/pay/`, { method: 'POST' })
}
