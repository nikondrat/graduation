import { apiFetch } from '../api/http'
import type { Photo } from '../data/photos'

export interface CartItemData {
  id: number
  photo: Photo
  licenseType: 'personal' | 'commercial'
  price: number
  addedAt: string
}

export interface CartData {
  id: number
  items: CartItemData[]
  total: number
  createdAt: string
  updatedAt: string
}

export interface CartCountData {
  count: number
}

export async function getCart(): Promise<CartData> {
  return apiFetch<CartData>('/cart/')
}

export async function getCartCount(): Promise<number> {
  const data = await apiFetch<CartCountData>('/cart/count/')
  return data.count
}

export async function addToCart(
  photoId: string,
  licenseType: string,
): Promise<CartItemData> {
  return apiFetch<CartItemData>('/cart/items/', {
    method: 'POST',
    body: JSON.stringify({ photo_id: photoId, license_type: licenseType }),
  })
}

export async function removeFromCart(itemId: number): Promise<void> {
  await apiFetch(`/cart/items/${itemId}/`, { method: 'DELETE' })
}

export async function updateCartItem(
  itemId: number,
  licenseType: string,
): Promise<CartItemData> {
  return apiFetch<CartItemData>(`/cart/items/${itemId}/`, {
    method: 'PATCH',
    body: JSON.stringify({ license_type: licenseType }),
  })
}

export async function checkout(): Promise<OrderData> {
  return apiFetch<OrderData>('/cart/checkout/', { method: 'POST' })
}

export interface OrderItemData {
  id: number
  photo: Photo
  licenseType: string
  price: number
}

export interface OrderData {
  id: number
  status: 'pending' | 'paid' | 'cancelled'
  total: number
  items: OrderItemData[]
  createdAt: string
  paidAt: string | null
}
