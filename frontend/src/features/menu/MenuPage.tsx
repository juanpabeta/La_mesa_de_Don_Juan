import { useMemo, useState, type FormEvent } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Check, Clock3, Plus, Search, SlidersHorizontal, Utensils, X } from 'lucide-react';
import { getApiError, isDemoMode } from '../../core/api/client';
import { resources } from '../../core/api/resources';
import { useResourceQuery } from '../../core/api/query';
import { demoMenu } from '../../core/data/demo';
import { useAuth } from '../../core/auth/AuthContext';
import type { MenuItem } from '../../core/types';
import { formatCOP } from '../../shared/utils/format';
import { PageHeader } from '../../shared/components/PageHeader';
import { Modal } from '../../shared/components/Modal';
import { useNotify } from '../../shared/components/ToastProvider';

export function MenuPage() {
  const queryClient = useQueryClient();
  const notify = useNotify();
  const { user } = useAuth();
  const admin = user?.roles.includes('Administrador') ?? false;
  const query = useResourceQuery('menu', resources.menu, demoMenu);
  const menu = query.data ?? [];
  const [category, setCategory] = useState('Todos');
  const [search, setSearch] = useState('');
  const [showUnavailable, setShowUnavailable] = useState(true);
  const [editing, setEditing] = useState<MenuItem | null | 'new'>(null);
  const categories = ['Todos', ...new Set(menu.map((dish) => dish.categoria))];
  const visible = useMemo(() => menu.filter((dish) => (category === 'Todos' || dish.categoria === category) && (showUnavailable || !dish.agotado) && `${dish.nombre} ${dish.categoria}`.toLowerCase().includes(search.toLowerCase())), [menu, category, search, showUnavailable]);

  const toggleUnavailable = async (dish: MenuItem) => {
    const agotado = !dish.agotado;
    try {
      if (!isDemoMode) await resources.updateDishAvailability(dish.id_plato, agotado);
      queryClient.setQueryData<MenuItem[]>(['menu'], (current = demoMenu) => current.map((item) => item.id_plato === dish.id_plato ? { ...item, agotado } : item));
      notify(agotado ? `${dish.nombre} marcado como agotado.` : `${dish.nombre} vuelve a estar disponible.`);
    } catch (error) { notify(getApiError(error, 'No se pudo cambiar la disponibilidad.'), 'info'); }
  };

  const saveDish = async (dish: MenuItem, isNew: boolean) => {
    try {
      if (!isDemoMode) {
        const payload = { nombre: dish.nombre, categoria: dish.categoria, precio: dish.precio, tiempo_estimado_min: dish.tiempo_estimado_min, activo: dish.activo };
        if (isNew) await resources.createDish(payload);
        else await resources.updateDish(dish.id_plato, payload);
      }
      queryClient.setQueryData<MenuItem[]>(['menu'], (current = demoMenu) => isNew ? [...current, dish] : current.map((item) => item.id_plato === dish.id_plato ? dish : item));
      setEditing(null);
      notify(isNew ? 'Producto creado en el menú.' : 'Producto actualizado.');
    } catch (error) { notify(getApiError(error, 'No se pudo guardar el producto.'), 'info'); }
  };

  return <>
    <PageHeader eyebrow="CATÁLOGO DEL RESTAURANTE" title="Menú" description="Mantén tu catálogo actualizado y sincronizado con cocina." actions={<>{admin && <button className="button button-primary" onClick={() => setEditing('new')}><Plus size={17} /> Nuevo producto</button>}</>} />
    <section className="menu-highlights">
      <article className="menu-highlight"><div className="menu-highlight-copy"><strong>{menu.length.toString().padStart(2, '0')}</strong><span>Productos en el menú</span></div><span className="menu-highlight-icon"><Utensils size={18} /></span></article>
      <article className="menu-highlight"><div className="menu-highlight-copy"><strong>{menu.filter((dish) => dish.agotado).length.toString().padStart(2, '0')}</strong><span>Marcados como agotados</span></div><span className="menu-highlight-icon orange"><Clock3 size={18} /></span></article>
      <article className="menu-highlight-note"><span className="live-dot" /><div><strong>Catálogo sincronizado</strong><span>Cambios visibles al instante en cocina</span></div></article>
    </section>
    <section className="panel menu-panel"><div className="menu-toolbar"><div className="filter-tabs menu-categories">{categories.map((item) => <button className={`filter-tab ${category === item ? 'selected' : ''}`} key={item} onClick={() => setCategory(item)}>{item}</button>)}</div><div className="menu-tools"><div className="table-search"><Search size={16} /><input placeholder="Buscar en el menú" aria-label="Buscar en el menú" value={search} onChange={(event) => setSearch(event.target.value)} /></div><button className={`button button-secondary button-small ${!showUnavailable ? 'button-toggled' : ''}`} onClick={() => setShowUnavailable((value) => !value)}><SlidersHorizontal size={15} />{showUnavailable ? 'Todos los productos' : 'Ocultar agotados'}</button></div></div><div className="menu-result-count">{category === 'Todos' ? 'Todos los productos' : category} <span>· {visible.length} productos</span></div><div className="menu-card-grid">{visible.map((dish) => <article className={`menu-item-card ${dish.agotado ? 'dish-unavailable' : ''}`} key={dish.id_plato}><div className="dish-card-top"><div className="dish-illustration">{dish.emoji ?? '🍽️'}</div><button className={`availability-toggle ${dish.agotado ? 'unavailable' : ''}`} onClick={() => void toggleUnavailable(dish)} aria-label={dish.agotado ? `Marcar ${dish.nombre} disponible` : `Marcar ${dish.nombre} agotado`} title={dish.agotado ? 'Agotado · clic para habilitar' : 'Disponible · clic para marcar agotado'}><span /></button></div><div className="dish-category">{dish.categoria}</div><div className="dish-name-row"><h3>{dish.nombre}</h3><span className="dish-price">{formatCOP(dish.precio)}</span></div><p>{dish.descripcion ?? 'Preparado al momento con ingredientes frescos.'}</p><div className="dish-card-footer"><span><Clock3 size={13} /> {dish.tiempo_estimado_min} min</span>{dish.agotado ? <span className="unavailable-label"><X size={13} /> Agotado</span> : <span className="available-label"><Check size={13} /> Disponible</span>}{admin && <button className="dish-edit" onClick={() => setEditing(dish)}>Editar</button>}</div></article>)}</div>{visible.length === 0 && <div className="empty-state"><span className="empty-emoji">🍽️</span><strong>No hay productos que coincidan</strong><p>Cambia la categoría o busca otro producto.</p></div>}</section>
    {editing && <DishModal dish={editing === 'new' ? null : editing} existingCategories={categories.filter((item) => item !== 'Todos')} onClose={() => setEditing(null)} onSave={(dish) => void saveDish(dish, editing === 'new')} />}
  </>;
}

function DishModal({ dish, existingCategories, onClose, onSave }: { dish: MenuItem | null; existingCategories: string[]; onClose: () => void; onSave: (dish: MenuItem) => void }) {
  const [name, setName] = useState(dish?.nombre ?? '');
  const [category, setCategory] = useState(dish?.categoria ?? existingCategories[0] ?? 'Platos fuertes');
  const [price, setPrice] = useState(dish?.precio.toString() ?? '');
  const [minutes, setMinutes] = useState(dish?.tiempo_estimado_min.toString() ?? '15');
  const [error, setError] = useState('');
  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!name.trim() || Number(price) <= 0 || Number(minutes) <= 0) { setError('Completa el nombre, precio y tiempo estimado.'); return; }
    const result: MenuItem = { id_plato: dish?.id_plato ?? Date.now(), nombre: name.trim(), categoria: category, precio: Number(price), tiempo_estimado_min: Number(minutes), activo: true, ...(dish?.agotado ? { agotado: true } : {}), ...(dish?.descripcion ? { descripcion: dish.descripcion } : {}), ...(dish?.emoji ? { emoji: dish.emoji } : {}) };
    onSave(result);
  };
  return <Modal title={dish ? 'Editar producto' : 'Nuevo producto'} description="Define la información que verá tu equipo." onClose={onClose}><form className="modal-body" onSubmit={submit}><label htmlFor="dish-name">Nombre del producto</label><input id="dish-name" className="form-input" value={name} onChange={(event) => setName(event.target.value)} placeholder="Ej. Bowl de salmón" required /><label htmlFor="dish-category">Categoría</label><input id="dish-category" className="form-input" list="dish-categories" value={category} onChange={(event) => setCategory(event.target.value)} required /><datalist id="dish-categories">{existingCategories.map((item) => <option key={item} value={item} />)}</datalist><div className="form-two-cols"><div><label htmlFor="dish-price">Precio (COP)</label><input id="dish-price" className="form-input" type="number" min="1" step="100" value={price} onChange={(event) => setPrice(event.target.value)} required /></div><div><label htmlFor="dish-time">Tiempo estimado (min)</label><input id="dish-time" className="form-input" type="number" min="1" max="180" value={minutes} onChange={(event) => setMinutes(event.target.value)} required /></div></div>{error && <p className="form-error">{error}</p>}<div className="modal-actions"><button type="button" className="button button-ghost" onClick={onClose}>Cancelar</button><button className="button button-primary"><Check size={15} /> Guardar producto</button></div></form></Modal>;
}
