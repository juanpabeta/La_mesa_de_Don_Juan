import type { Incident, MenuItem, Order, Table, User } from '../types';

export const demoUser: User = {
  id_usuario: 1,
  nombres: 'Mariana',
  apellidos: 'Gómez',
  correo: 'mariana@kitchenflow.co',
  estado: true,
  roles: ['Administrador', 'Mesero'],
};

export const demoTables: Table[] = [
  { id_mesa: 1, numero_mesa: 1, zona: 'Salón', capacidad: 2, estado: 'OCUPADA', activa: true, tiempo: '24 min', total: 64800 },
  { id_mesa: 2, numero_mesa: 2, zona: 'Salón', capacidad: 4, estado: 'LIBRE', activa: true },
  { id_mesa: 3, numero_mesa: 3, zona: 'Salón', capacidad: 4, estado: 'OCUPADA', activa: true, tiempo: '18 min', total: 92500 },
  { id_mesa: 4, numero_mesa: 4, zona: 'Salón', capacidad: 6, estado: 'POR_LIMPIAR', activa: true },
  { id_mesa: 5, numero_mesa: 5, zona: 'Terraza', capacidad: 2, estado: 'RESERVADA', activa: true },
  { id_mesa: 6, numero_mesa: 6, zona: 'Terraza', capacidad: 4, estado: 'OCUPADA', activa: true, tiempo: '32 min', total: 118000 },
  { id_mesa: 7, numero_mesa: 7, zona: 'Terraza', capacidad: 4, estado: 'LIBRE', activa: true },
  { id_mesa: 8, numero_mesa: 8, zona: 'Barra', capacidad: 2, estado: 'LIBRE', activa: true },
  { id_mesa: 9, numero_mesa: 9, zona: 'Barra', capacidad: 2, estado: 'OCUPADA', activa: true, tiempo: '12 min', total: 36700 },
  { id_mesa: 10, numero_mesa: 10, zona: 'Barra', capacidad: 2, estado: 'LIBRE', activa: true },
  { id_mesa: 11, numero_mesa: 11, zona: 'Salón', capacidad: 4, estado: 'LIBRE', activa: true },
  { id_mesa: 12, numero_mesa: 12, zona: 'Terraza', capacidad: 6, estado: 'POR_LIMPIAR', activa: true },
];

export const demoMenu: MenuItem[] = [
  { id_plato: 1, nombre: 'Bowl de salmón', categoria: 'Favoritos', precio: 38900, tiempo_estimado_min: 14, activo: true, descripcion: 'Salmón sellado, arroz de coco y aguacate.', emoji: '🍣' },
  { id_plato: 2, nombre: 'Pasta trufada', categoria: 'Favoritos', precio: 42900, tiempo_estimado_min: 18, activo: true, descripcion: 'Tagliatelle, crema de hongos y aceite de trufa.', emoji: '🍝' },
  { id_plato: 3, nombre: 'Hamburguesa de la casa', categoria: 'Platos fuertes', precio: 35900, tiempo_estimado_min: 16, activo: true, descripcion: 'Res madurada, cheddar, cebolla caramelizada.', emoji: '🍔' },
  { id_plato: 4, nombre: 'Pollo al carbón', categoria: 'Platos fuertes', precio: 32900, tiempo_estimado_min: 19, activo: true, descripcion: 'Pechuga a la brasa con vegetales de temporada.', emoji: '🍗' },
  { id_plato: 5, nombre: 'Tostadas de aguacate', categoria: 'Entradas', precio: 18900, tiempo_estimado_min: 8, activo: true, descripcion: 'Pan de masa madre, aguacate y huevo pochado.', emoji: '🥑' },
  { id_plato: 6, nombre: 'Burrata & tomates', categoria: 'Entradas', precio: 24600, tiempo_estimado_min: 7, activo: true, descripcion: 'Burrata fresca, tomates heirloom y albahaca.', emoji: '🍅' },
  { id_plato: 7, nombre: 'Limonada de coco', categoria: 'Bebidas', precio: 9500, tiempo_estimado_min: 3, activo: true, descripcion: 'Limón natural y crema de coco.', emoji: '🥥' },
  { id_plato: 8, nombre: 'Cheesecake de maracuyá', categoria: 'Postres', precio: 14500, tiempo_estimado_min: 4, activo: true, descripcion: 'Cheesecake cremoso con coulis de maracuyá.', emoji: '🍰' },
  { id_plato: 9, nombre: 'Risotto de setas', categoria: 'Platos fuertes', precio: 36900, tiempo_estimado_min: 22, activo: true, agotado: true, descripcion: 'Arroz arborio, setas silvestres y parmesano.', emoji: '🍄' },
];

const now = Date.now();
export const demoOrders: Order[] = [
  { id_pedido: 1048, id_mesa: 3, numero_mesa: 3, mesero: 'Valentina Ríos', estado: 'EN_PREPARACION', fecha_hora_creacion: new Date(now - 14 * 60_000).toISOString(), es_retrasado: false, detalles: [{ id_detalle: 1, id_plato: 2, nombre: 'Pasta trufada', cantidad: 2, precio_unitario: 42900 }, { id_detalle: 2, id_plato: 7, nombre: 'Limonada de coco', cantidad: 2, precio_unitario: 9500 }] },
  { id_pedido: 1047, id_mesa: 6, numero_mesa: 6, mesero: 'Santiago Mejía', estado: 'PENDIENTE', fecha_hora_creacion: new Date(now - 8 * 60_000).toISOString(), es_retrasado: true, detalles: [{ id_detalle: 3, id_plato: 4, nombre: 'Pollo al carbón', cantidad: 2, precio_unitario: 32900 }, { id_detalle: 4, id_plato: 6, nombre: 'Burrata & tomates', cantidad: 1, precio_unitario: 24600 }] },
  { id_pedido: 1046, id_mesa: 1, numero_mesa: 1, mesero: 'Valentina Ríos', estado: 'LISTO', fecha_hora_creacion: new Date(now - 20 * 60_000).toISOString(), es_retrasado: false, detalles: [{ id_detalle: 5, id_plato: 3, nombre: 'Hamburguesa de la casa', cantidad: 1, precio_unitario: 35900 }, { id_detalle: 6, id_plato: 5, nombre: 'Tostadas de aguacate', cantidad: 1, precio_unitario: 18900 }] },
  { id_pedido: 1045, id_mesa: 9, numero_mesa: 9, mesero: 'Camilo Torres', estado: 'PENDIENTE', fecha_hora_creacion: new Date(now - 5 * 60_000).toISOString(), es_retrasado: false, detalles: [{ id_detalle: 7, id_plato: 1, nombre: 'Bowl de salmón', cantidad: 1, precio_unitario: 38900 }] },
  { id_pedido: 1044, id_mesa: 5, numero_mesa: 5, mesero: 'Santiago Mejía', estado: 'ENTREGADO', fecha_hora_creacion: new Date(now - 44 * 60_000).toISOString(), es_retrasado: false, detalles: [{ id_detalle: 8, id_plato: 8, nombre: 'Cheesecake de maracuyá', cantidad: 2, precio_unitario: 14500 }] },
];

export const demoIncidents: Incident[] = [
  { id_incidencia: 208, id_pedido: 1046, id_usuario: 3, tipo_error: 'Equipo', tipo: 'Equipo', descripcion: 'La freidora de la estación caliente no mantiene temperatura.', prioridad: 'ALTA', estado: 'EN_REVISION', creado_por: 'Camilo Torres', fecha_hora: new Date(now - 18 * 60_000).toISOString(), fecha_registro: new Date(now - 18 * 60_000).toISOString() },
  { id_incidencia: 207, id_pedido: 1045, id_usuario: 3, tipo_error: 'Inventario', tipo: 'Inventario', descripcion: 'Agotado el risotto de setas por falta de hongos.', prioridad: 'MEDIA', estado: 'ABIERTA', creado_por: 'Valentina Ríos', fecha_hora: new Date(now - 52 * 60_000).toISOString(), fecha_registro: new Date(now - 52 * 60_000).toISOString() },
  { id_incidencia: 206, id_pedido: 1044, id_usuario: 3, tipo_error: 'Servicio', tipo: 'Servicio', descripcion: 'Cliente solicita revisión de cuenta en mesa 4.', prioridad: 'BAJA', estado: 'RESUELTA', creado_por: 'Santiago Mejía', fecha_hora: new Date(now - 110 * 60_000).toISOString(), fecha_registro: new Date(now - 110 * 60_000).toISOString() },
];

export const demoUsers: User[] = [
  demoUser,
  { id_usuario: 2, nombres: 'Valentina', apellidos: 'Ríos', correo: 'valentina@kitchenflow.co', estado: true, roles: ['Mesero'] },
  { id_usuario: 3, nombres: 'Camilo', apellidos: 'Torres', correo: 'camilo@kitchenflow.co', estado: true, roles: ['Cocinero'] },
  { id_usuario: 4, nombres: 'Santiago', apellidos: 'Mejía', correo: 'santiago@kitchenflow.co', estado: true, roles: ['Mesero', 'Cajero'] },
  { id_usuario: 5, nombres: 'Lucía', apellidos: 'Pardo', correo: 'lucia@kitchenflow.co', estado: false, roles: ['Cajero'] },
];
